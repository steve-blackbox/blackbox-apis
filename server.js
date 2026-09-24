// 🌌 BLACKBOX MICROSERVICES CORE ENGINE — PRODUCTION NODE V6
const express = require('express');
const cors = require('cors');
const path = require('path');
const crypto = require('crypto');
const { Paddle, Environment, EventName } = require('@paddle/paddle-node-sdk');

// 📨 EXPÉDITEUR D'E-MAILS RESEND INITIALISÉ
const { Resend } = require('resend');
const resend = new Resend(process.env.RESEND_API_KEY);

// 📊 SUIVI DE TRACTION (ventes persistantes + checkpoints J+30/60/90)
const { recordSale, getStats, saveLicense, isValidLicense, getLicenseByKey, getAllActiveLicenseMeta, deactivateLicensesByPaddleSubscription, DEMO_LICENSE_KEY, seedDemoLicense } = require('./lib/db');

// 🗂️ CATALOGUE DES 3 CATÉGORIES DE ROBOTS (doit rester synchronisé avec `robotsCatalog`
// dans public/index.html). Sert à restreindre l'accès des licences SOLO CORE à une
// seule catégorie (4 robots), contrairement à LABS ALL-ACCESS qui couvre les 12.
const ROBOT_CATEGORIES = {
    'Privacy & PII Protection': ['log_sanitizer', 'pii_masker', 'phone_sanitizer', 'ip_anonymizer'],
    'Security & Link Integrity': ['bot_detector', 'crypto_verify', 'link_signer', 'link_validator'],
    'Data & Media Utilities': ['csv_dedupe', 'exif_cloak', 'timezone_converter', 'uptime_check'],
};

// 🅿️ ENCAPSULATION SECURISEE PADDLE (processeur de paiement unique — Stripe retiré)
// PADDLE_ENV vaut 'sandbox' pendant les tests, puis 'production' une fois le compte
// Paddle basculé en mode live (voir .env). Le client n'est initialisé que si la clé
// est présente, pour ne jamais planter le serveur si la configuration est incomplète.
const paddleClient = process.env.PADDLE_API_KEY
    ? new Paddle(process.env.PADDLE_API_KEY, {
        environment: process.env.PADDLE_ENV === 'production' ? Environment.production : Environment.sandbox,
    })
    : null;

const app = express();

// 🛡️ MIDDLEWARES STRUCTURAUX DE SOUTE
app.use(cors({ origin: '*' }));

// 📨 Envoie l'e-mail d'activation de licence
async function sendLicenseActivationEmail({ email, name, licenseKey, category }) {
    const accessLine = category
        ? `<p>Votre licence <strong>SOLO CORE</strong> donne accès à la catégorie : <strong>${category}</strong> (4 robots).</p>`
        : `<p>Votre licence <strong>LABS ALL-ACCESS</strong> donne accès aux 3 catégories (12 robots).</p>`;
    await resend.emails.send({
        from: 'BlackBox Audio Labs <activation@blackbox-apis.com>',
        to: [email],
        subject: '🔥 Activation de votre licence BlackBox Audio Labs',
        html: `
            <div style="font-family: sans-serif; padding: 20px; background: #000; color: #fff; border-radius: 8px;">
                <h2 style="color: #00ffcc;">Félicitations ${name} !</h2>
                <p>Votre paiement a été sécurisé avec succès. Votre réacteur d'automatisation est prêt.</p>
                <div style="background: #111; padding: 15px; border-left: 4px solid #00ffcc; margin: 20px 0; font-family: monospace; font-size: 16px; letter-spacing: 1px;">
                    <strong>VOTRE CLÉ DE LICENCE :</strong> ${licenseKey}
                </div>
                ${accessLine}
                <p>Utilisez-la dans l'en-tête <code>Authorization: Bearer ${licenseKey}</code> de vos appels API (voir la <a href="https://blackbox-apis.com/docs.html" style="color:#00ffcc;">documentation</a>).</p>
                <p style="color: #888; font-size: 12px;">LLC BlackBox Audio Labs — Wyoming, USA</p>
            </div>
        `
    });
}

// 📡 1. ROUTE DU WEBHOOK PADDLE (PLINDÉE AVANT EXPRESS.JSON)
// Le corps doit rester "brut" (non parsé par express.json) pour que la vérification de
// signature Paddle (en-tête "paddle-signature") soit valide.
app.post('/v1/webhook/paddle', express.raw({ type: 'application/json' }), async (req, res) => {
    if (!paddleClient) {
        console.error('❌ Webhook Paddle reçu mais PADDLE_API_KEY absente côté serveur.');
        return res.status(503).send('Paddle non configuré côté serveur.');
    }

    const signature = req.headers['paddle-signature'];
    let paddleEvent;

    try {
        // Validation forensique du signal Paddle avec le secret de la destination de
        // notification (voir PADDLE_WEBHOOK_SECRET dans .env / Render).
        paddleEvent = await paddleClient.webhooks.unmarshal(req.body.toString(), process.env.PADDLE_WEBHOOK_SECRET, signature);
    } catch (err) {
        console.error(`❌ Erreur Webhook Paddle Signature: ${err.message}`);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // 🟢 CASH SÉCURISÉ : la transaction est validée par Paddle (abonnement mensuel récurrent)
    if (paddleEvent.eventType === EventName.TransactionCompleted) {
        const transaction = paddleEvent.data;
        const purchasedPlan = transaction.customData?.plan || 'labs';

        // 🗂️ Catégorie choisie par le client au moment du checkout (uniquement pour le
        // plan SOLO CORE — LABS ALL-ACCESS n'a pas besoin de restriction, il couvre tout).
        // Si le plan est "core" mais la catégorie transmise est invalide/absente, on la
        // laisse à null : le middleware requireLicense refusera alors l'accès aux robots
        // tant qu'aucune catégorie valide n'est associée à la clé (fail-safe).
        const purchasedCategory = purchasedPlan === 'core' && ROBOT_CATEGORIES[transaction.customData?.category]
            ? transaction.customData.category
            : null;

        // Le nom/e-mail du client n'est pas inclus directement dans la notification de
        // transaction : on va le chercher via l'API Customers avec le customerId fourni.
        let customerEmail = null;
        let customerName = 'Client BlackBox';
        try {
            if (transaction.customerId) {
                const customer = await paddleClient.customers.get(transaction.customerId);
                customerEmail = customer.email;
                customerName = customer.name || customerName;
            }
        } catch (customerError) {
            console.error('❌ Échec récupération du client Paddle:', customerError);
        }

        if (!customerEmail) {
            console.error(`❌ Transaction Paddle ${transaction.id} complétée mais e-mail client introuvable — licence NON générée.`);
            return res.json({ received: true });
        }

        // 🔑 GÉNÉRATION DE LA CLÉ DE LICENCE EXCLUSIVE BLACKBOX
        const uniqueId = crypto.randomBytes(4).toString('hex').toUpperCase();
        const licenseKey = `BB-${purchasedPlan.toUpperCase()}-CORE-${uniqueId}`;

        if (global.activeLicenseKeys) {
            global.activeLicenseKeys.add(licenseKey);
        }
        if (global.licenseMeta) {
            global.licenseMeta.set(licenseKey, { plan: purchasedPlan, category: purchasedCategory });
        }

        try {
            saveLicense({
                licenseKey,
                email: customerEmail,
                plan: purchasedPlan,
                category: purchasedCategory,
                paddleSubscriptionId: transaction.subscriptionId,
                paddleCustomerId: transaction.customerId,
            });
        } catch (licenseError) {
            console.error('❌ Échec enregistrement persistant de la licence (Paddle):', licenseError);
        }

        try {
            recordSale({
                email: customerEmail,
                plan: purchasedPlan,
                amountCents: parseInt(transaction.details?.totals?.total || '0', 10),
                currency: (transaction.currencyCode || 'usd').toLowerCase(),
                licenseKey,
            });
        } catch (dbError) {
            console.error('❌ Échec enregistrement vente en base de traction (Paddle):', dbError);
        }

        console.log(`🚀 [PADDLE] Paiement Validé pour ${customerEmail}! Licence Générée: ${licenseKey}`);

        try {
            await sendLicenseActivationEmail({ email: customerEmail, name: customerName, licenseKey, category: purchasedCategory });
            console.log(`📧 E-mail de licence envoyé avec succès à ${customerEmail}`);
        } catch (emailError) {
            console.error(`❌ Échec de l'envoi de l'e-mail Resend (Paddle):`, emailError);
        }
    }

    // 🔴 ANNULATION D'ABONNEMENT PADDLE : coupe l'accès immédiatement (évite un accès
    // à vie après résiliation).
    if (paddleEvent.eventType === EventName.SubscriptionCanceled) {
        const subscription = paddleEvent.data;
        const revoked = deactivateLicensesByPaddleSubscription(subscription.id);
        if (revoked > 0) {
            rebuildLicenseCaches();
        }
        console.log(`🚫 [PADDLE] Abonnement ${subscription.id} annulé — ${revoked} licence(s) désactivée(s).`);
    }

    // 🟠 ÉCHEC/RETARD DE PAIEMENT MENSUEL PADDLE : journalisation seule, sans couper l'accès
    // immédiatement (Paddle retente automatiquement avant d'envoyer subscription.canceled).
    if (paddleEvent.eventType === EventName.SubscriptionPastDue) {
        const subscription = paddleEvent.data;
        console.log(`⚠️ [PADDLE] Abonnement ${subscription.id} en retard de paiement.`);
    }

    res.json({ received: true });
});

// 📡 2. TRADUCTEURS DE PAYLOADS POUR LES AUTRES ROUTES SOUCHÉES
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// 🧠 ARCHITECTURE IN-MEMORY : cache rapide, rechargé depuis la base persistante à chaque démarrage
// (corrige le bug où un redémarrage/redéploiement Render effaçait toutes les licences vendues)
// - activeLicenseKeys : Set des clés valides (contrôle d'accès rapide dans requireLicense)
// - licenseMeta : Map clé -> { plan, category } (restriction par catégorie pour SOLO CORE)
function rebuildLicenseCaches() {
    const rows = getAllActiveLicenseMeta();
    global.activeLicenseKeys = new Set(['BB-ADMIN-CORE-99', ...rows.map((r) => r.license_key)]);
    global.licenseMeta = new Map(rows.map((r) => [r.license_key, { plan: r.plan, category: r.category }]));
}
seedDemoLicense(); // ré-insère la clé démo publique (Postman) à chaque démarrage, quel que soit l'état du disque
rebuildLicenseCaches();
console.log(`🔑 ${global.activeLicenseKeys.size} licence(s) active(s) rechargée(s) depuis la base persistante.`);

// 🎟️ QUOTA DE LA CLÉ DÉMO PUBLIQUE : compteur en mémoire, remis à zéro chaque jour UTC.
// Volontairement généreux pour laisser tester chaque robot, mais strictement plafonné
// pour ne jamais devenir un accès gratuit illimité une fois la clé publiée sur Postman.
const DEMO_DAILY_LIMIT = 50;
const demoUsage = { day: null, count: 0 };
function checkDemoRateLimit() {
    const today = new Date().toISOString().slice(0, 10);
    if (demoUsage.day !== today) {
        demoUsage.day = today;
        demoUsage.count = 0;
    }
    demoUsage.count += 1;
    return demoUsage.count <= DEMO_DAILY_LIMIT;
}

// 🔎 Route de vérification de licence appelée par le bouton "VERIFY" du site (public/index.html)
app.post('/api/verify-license', (req, res) => {
    const key = (req.body?.key || '').trim().toUpperCase();
    if (!key) {
        return res.status(400).json({ success: false, message: 'Missing key' });
    }
    // Vérifie d'abord le cache mémoire (rapide), puis la base en dernier recours
    const valid = global.activeLicenseKeys.has(key) || isValidLicense(key);
    if (valid) {
        global.activeLicenseKeys.add(key); // rafraîchit le cache si trouvé seulement en base
        if (!global.licenseMeta.has(key)) {
            const row = getLicenseByKey(key);
            if (row) global.licenseMeta.set(key, { plan: row.plan, category: row.category });
        }
    }
    return res.json({ success: valid });
});

app.post('/v1/checkout', async (req, res) => {
    if (!paddleClient) {
        return res.status(503).json({ error: 'Paddle non configuré côté serveur (PADDLE_API_KEY manquante).' });
    }

    try {
        const { plan, endpoint_target, category } = req.body;

        let targetPriceId = '';
        const planType = plan ? plan.toLowerCase().trim() : '';

        if (planType === 'core' || planType === 'solo' || planType === 'matrix' || planType === 'single') {
            targetPriceId = process.env.PADDLE_PRICE_SOLO_MONTHLY; // 🟢 SOLO — 12$/mois
        } else if (planType === 'labs' || planType === 'premium' || planType === 'allaccess' || planType === 'all-access' || planType === 'adblock_bypass') {
            targetPriceId = process.env.PADDLE_PRICE_ALLACCESS_MONTHLY; // 🔵 ALL-ACCESS — 29$/mois
        } else {
            console.log("👉 Alerte soute : planType inconnu ou manquant (Paddle). Redirection forcé sur All Access. Input reçu :", planType);
            targetPriceId = process.env.PADDLE_PRICE_ALLACCESS_MONTHLY;
        }

        if (!targetPriceId) {
            console.error('❌ Aucun PADDLE_PRICE_* configuré côté serveur pour le plan demandé:', planType);
            return res.status(500).json({ error: 'Configuration de prix Paddle manquante côté serveur.' });
        }

        // 🗂️ Catégorie choisie (uniquement pertinente pour SOLO CORE — voir menu déroulant
        // sur la carte de prix dans public/index.html). Ignorée/absente pour LABS ALL-ACCESS.
        const requestedCategory = (planType === 'core' && ROBOT_CATEGORIES[category]) ? category : null;
        if (planType === 'core' && !requestedCategory) {
            return res.status(400).json({ error: 'Merci de choisir une catégorie de robots avant de continuer.' });
        }

        // Création de la transaction Paddle : Paddle renvoie une URL de paiement (checkout.url)
        // vers laquelle on redirige le client (ouverture de l'overlay Paddle.js côté front).
        // Le retour après paiement réussi est géré côté front par "successUrl" dans
        // Paddle.Initialize (voir public/index.html) — pas ici.
        const transaction = await paddleClient.transactions.create({
            items: [{ priceId: targetPriceId, quantity: 1 }],
            customData: {
                plan: planType || 'labs',
                category: requestedCategory,
                endpoint_target: endpoint_target || 'none',
            },
        });

        res.json({ url: transaction.checkout?.url || null });

    } catch (error) {
        console.error('Erreur forensique lors de la création du Checkout Paddle:', error);
        res.status(500).json({ error: 'Erreur interne du serveur de soute' });
    }
});

// 🛰️ DÉPLOIEMENT FINAL FORCE : ALIGNEMENT DES FICHIERS EN DUR (0% FLASH)
// 📁 API ENDPOINTS: STANDALONE INDEPENDENT PRODUCTION ROUTING (0% FLASH)
app.get('/docs', (req, res) => res.sendFile(path.join(__dirname, 'public', 'docs.html')));
app.get('/terms.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'terms.html')));
app.get('/privacy.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'privacy.html')));
// 🔄 REDIRECTION DE SECOURS : RENVOIE DIRECTEMENT SUR L'ACCUEIL EN CAS D'ANNULATION
app.get('/cancel.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

// 🔑 MIDDLEWARE DE LICENCE : vérifie la clé fournie via l'en-tête Authorization: Bearer <clé>
// (ou via le champ 'token' du corps de la requête, pour compatibilité).
// 📊 TABLEAU DE BORD DE TRACTION (accès protégé par clé admin)
// Clé attendue en en-tête "x-admin-key" (à définir via la variable d'env ADMIN_DASHBOARD_KEY).
function requireAdminKey(req, res, next) {
    const expected = process.env.ADMIN_DASHBOARD_KEY;
    const provided = req.headers['x-admin-key'];

    if (!expected) {
        return res.status(503).json({ error: 'ADMIN_DASHBOARD_KEY non configurée sur le serveur.' });
    }
    if (!provided || provided !== expected) {
        return res.status(401).json({ error: 'Clé admin invalide ou manquante.' });
    }
    next();
}

app.get('/api/admin/stats', requireAdminKey, (req, res) => {
    try {
        res.json(getStats());
    } catch (statsError) {
        console.error('❌ Erreur récupération stats:', statsError);
        res.status(500).json({ error: 'Erreur interne lors du calcul des statistiques.' });
    }
});

app.get('/admin/dashboard', (req, res) => res.sendFile(path.join(__dirname, 'public', 'admin-dashboard.html')));

// 🔑 MIDDLEWARE DE LICENCE : vérifie la clé fournie via l'en-tête "Authorization: Bearer <clé>"
// (ou via le champ 'token' du corps de la requête, pour compatibilité), puis, pour les
// licences SOLO CORE, restreint l'accès à la seule catégorie de robots achetée.
function requireLicense(robotName) {
    const robotCategory = Object.keys(ROBOT_CATEGORIES).find((cat) => ROBOT_CATEGORIES[cat].includes(robotName));

    return function (req, res, next) {
        const authHeader = req.headers['authorization'] || '';
        const bearerToken = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : null;
        const token = bearerToken || req.body?.token;

        if (!token || !global.activeLicenseKeys.has(token)) {
            return res.status(401).json({ success: false, message: "» INGRESS REFUSED: Invalid or missing license key." });
        }

        const meta = global.licenseMeta.get(token);

        // 🎟️ Clé démo publique (Postman API Network) : quota journalier strict, jamais
        // un accès illimité — voir DEMO_DAILY_LIMIT ci-dessus.
        if (token === DEMO_LICENSE_KEY && !checkDemoRateLimit()) {
            return res.status(429).json({
                success: false,
                message: `» DEMO QUOTA EXCEEDED: This public demo key is capped at ${DEMO_DAILY_LIMIT} requests/day. Get your own key at https://blackbox-apis.com/.`,
            });
        }

        // Une licence LABS ALL-ACCESS (ou la clé admin, sans meta) a accès à tout.
        // Une licence SOLO CORE ("core") n'a accès qu'à la catégorie achetée.
        if (meta && meta.plan === 'core' && meta.category !== robotCategory) {
            return res.status(403).json({
                success: false,
                message: `» ACCESS DENIED: Your SOLO CORE license only covers the "${meta.category || 'unassigned'}" category.`,
            });
        }

        next();
    };
}

// 🤖 CATALOGUE DES 12 ROBOTS RÉELS : chaque endpoint est monté sous /v1/<nom_du_robot>
// et protégé par la clé de licence active. Les fichiers correspondants contiennent
// la vraie logique métier (parsing CSV réel, checksum crypto réel, retrait EXIF binaire réel, etc.).
const realRobotRoutes = [
    'log_sanitizer',
    'pii_masker',
    'phone_sanitizer',
    'ip_anonymizer',
    'bot_detector',
    'crypto_verify',
    'link_signer',
    'link_validator',
    'csv_dedupe',
    'exif_cloak',
    'timezone_converter',
    'uptime_check'
];

realRobotRoutes.forEach((robotName) => {
    app.use(`/v1/${robotName}`, requireLicense(robotName), require(`./${robotName}`));
});

// 🎛️ IGNITION DES RÉACTEURS SUR LE PORT CLOUD REGLÉ PAR RENDER
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`[🚀 SERVER LIVE]: Port ${PORT}`);
});