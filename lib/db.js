// 📊 BLACKBOX TRACTION DB — Suivi persistant des ventes/checkpoints J+30/60/90
// Stockage local SQLite (fichier data/blackbox.db). ⚠️ Sur Render, ce fichier
// est perdu à chaque redéploiement sauf si un "Persistent Disk" est monté sur
// le dossier /data (Render > Service > Disks). Voir README_TRACKING.md.
const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

const DATA_DIR = path.join(__dirname, '..', 'data');
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

const db = new Database(path.join(DATA_DIR, 'blackbox.db'));
db.pragma('journal_mode = WAL');

db.exec(`
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        plan TEXT,
        amount_cents INTEGER NOT NULL DEFAULT 0,
        currency TEXT NOT NULL DEFAULT 'usd',
        license_key TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    );

    -- 🔑 Licences persistantes : survit aux redémarrages/redéploiements du serveur
    -- (contrairement à l'ancien registre in-memory qui était vidé à chaque restart)
    CREATE TABLE IF NOT EXISTS licenses (
        license_key TEXT PRIMARY KEY,
        email TEXT,
        plan TEXT,
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
`);

// 🚀 Date de lancement figée au premier démarrage (sert de J0 pour les checkpoints)
function getLaunchDate() {
    const envDate = process.env.LAUNCH_DATE; // format YYYY-MM-DD, override manuel possible
    if (envDate) return envDate;

    const row = db.prepare('SELECT value FROM config WHERE key = ?').get('launch_date');
    if (row) return row.value;

    const today = new Date().toISOString().slice(0, 10);
    db.prepare('INSERT INTO config (key, value) VALUES (?, ?)').run('launch_date', today);
    return today;
}

function recordSale({ email, plan, amountCents, currency, licenseKey }) {
    db.prepare(`
        INSERT INTO sales (email, plan, amount_cents, currency, license_key)
        VALUES (?, ?, ?, ?, ?)
    `).run(email || null, plan || null, amountCents || 0, currency || 'usd', licenseKey || null);
}

function getStats() {
    const launchDate = getLaunchDate();
    const daysSinceLaunch = Math.floor(
        (Date.now() - new Date(launchDate + 'T00:00:00Z').getTime()) / 86400000
    );

    const totals = db.prepare(`
        SELECT COUNT(*) AS count, COALESCE(SUM(amount_cents), 0) AS total_cents
        FROM sales
    `).get();

    const byPlan = db.prepare(`
        SELECT plan, COUNT(*) AS count, COALESCE(SUM(amount_cents), 0) AS total_cents
        FROM sales GROUP BY plan
    `).all();

    const last30 = db.prepare(`
        SELECT COUNT(*) AS count, COALESCE(SUM(amount_cents), 0) AS total_cents
        FROM sales WHERE created_at >= datetime('now', '-30 days')
    `).get();

    const recent = db.prepare(`
        SELECT email, plan, amount_cents, currency, created_at
        FROM sales ORDER BY created_at DESC LIMIT 20
    `).all();

    // 🎯 Checkpoints fixés dans la ligne directrice (voir utiles/ligne_directrice_strategie.md)
    const revenueEur = totals.total_cents / 100; // approximation (pas de conversion de devise réelle)
    let checkpoint = { day: daysSinceLaunch, status: 'EN_COURS', label: '' };

    if (daysSinceLaunch <= 30) {
        checkpoint.label = 'Checkpoint J+30 — objectif : trafic + premiers signes d\'intérêt (voir Umami)';
    } else if (daysSinceLaunch <= 60) {
        checkpoint.label = 'Checkpoint J+60 — objectif : ≥ 1-3 clients payants, ≥ 50-150 €';
        checkpoint.status = totals.count >= 1 ? 'OK' : 'ALERTE';
    } else if (daysSinceLaunch <= 90) {
        checkpoint.label = 'Checkpoint J+90 — décision Go/No-Go';
        if (revenueEur >= 300) checkpoint.status = 'GO';
        else if (revenueEur >= 50) checkpoint.status = 'ZONE_GRISE';
        else checkpoint.status = 'NO_GO';
    } else {
        checkpoint.label = 'Au-delà de J+90 — suivi continu vers le seuil de démission (4750-5000 €/mois)';
        checkpoint.status = revenueEur >= 4750 ? 'SEUIL_ATTEINT' : 'EN_COURS';
    }

    return {
        launchDate,
        daysSinceLaunch,
        totalSales: totals.count,
        totalRevenue: revenueEur,
        last30DaysSales: last30.count,
        last30DaysRevenue: last30.total_cents / 100,
        byPlan: byPlan.map(p => ({ plan: p.plan || 'inconnu', count: p.count, revenue: p.total_cents / 100 })),
        recent,
        checkpoint,
    };
}

// 💾 Enregistre une licence de façon permanente (appelé à chaque vente validée par Stripe)
function saveLicense({ licenseKey, email, plan }) {
    db.prepare(`
        INSERT INTO licenses (license_key, email, plan, active)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(license_key) DO UPDATE SET active = 1
    `).run(licenseKey, email || null, plan || null);
}

// ✅ Vérifie si une clé est valide et active (source de vérité en base, pas seulement en mémoire)
function isValidLicense(licenseKey) {
    const row = db.prepare('SELECT active FROM licenses WHERE license_key = ?').get(licenseKey);
    return !!row && row.active === 1;
}

// 🔄 Recharge toutes les clés actives depuis la base au démarrage du serveur
// (permet de reconstruire le cache in-memory après un redémarrage/redéploiement)
function getAllActiveLicenseKeys() {
    return db.prepare('SELECT license_key FROM licenses WHERE active = 1').all().map((r) => r.license_key);
}

module.exports = { recordSale, getStats, getLaunchDate, saveLicense, isValidLicense, getAllActiveLicenseKeys };
