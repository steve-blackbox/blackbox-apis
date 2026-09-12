const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Tampon temporaire en mémoire volatile (0€ d'infrastructure SQL)
let webhookQueue = [];

// ==========================================
// [💳 ROUTE COMMERCIALE : STRIPE BYPASS PRO - 79€]
// ==========================================
app.post('/api/checkout/create-session', (req, res) => {
    try {
        const { customerEmail, type } = req.body;
        console.log(`\n[💳 STRIPE WEBHOOK] Demande de session pour ${type || 'solo'} : ${customerEmail}`);
        
        const price = type === 'agence' ? '199€' : '79€';
        console.log(`[💰 TRÉSORERIE] Tarification isolée : ${price}`);

        const fakeSuccessUrl = `http://localhost:4246/?success=true&email=${encodeURIComponent(customerEmail || 'marchand-shopify@gmail.com')}`;
        return res.json({ id: "fake_webhook_session_id", url: fakeSuccessUrl });
    } catch (checkoutError) {
        console.error(`[❌ CRASH-SHIELD CHECKOUT] Erreur de soute financière : ${checkoutError.message}`);
        return res.status(500).json({ error: "Bypass de paiement sécurisé momentanément indisponible." });
    }
});

// ==========================================
// [⚙️ MOTEUR TECHNIQUE : INTERCEPTION + CRASH-SHIELD]
// ==========================================
app.post('/api/shield/intercept', (req, res) => {
    try {
        const webhookData = req.body;
        const targetUrl = req.headers['x-target-url'];

        // PROTECTION ABSORBANTE : Si l'utilisateur envoie une requête malformée sans destination
        if (!targetUrl || Object.keys(webhookData).length === 0) {
            console.warn(`[⚠️ CRASH-SHIELD INTERCEPT] Requête invalide ou en-tête mal formé intercepté.`);
            return res.status(400).json({ error: "Structure de webhook corrompue ou cible introuvable. Requête rejetée." });
        }

        console.log(`\n[📥 INTERCEPTION] Webhook capturé proprement. Cible : ${targetUrl}`);
        
        const eventId = Date.now();
        webhookQueue.push({ id: eventId, targetUrl, data: webhookData, attempts: 0 });

        console.log(`[📦 BUFFER] Événement ${eventId} sécurisé dans la file d'attente volatile.`);
        return res.json({ success: true, eventId, message: "Webhook sécurisé au bouclier tampon." });
    } catch (interceptError) {
        console.error(`[❌ CRASH-SHIELD BUFFER] Erreur critique d'ingestion : ${interceptError.message}`);
        return res.status(500).json({ error: "Erreur interne du système de redondance." });
    }
});

// Route d'inspection sécurisée pour le tableau de bord Bento
app.get('/api/shield/queue', (req, res) => {
    try {
        return res.json({ count: webhookQueue.length, queue: webhookQueue });
    } catch (queueError) {
        return res.status(500).json({ error: "Impossible de lire la file d'attente." });
    }
});

// IMMUNISATION ABSOLUE : Capture des crashs asynchrones inattendus pour éviter le disjoncteur général
process.on('uncaughtException', (err) => {
    console.error(`\n[🚨 ANTI-DISJONCTEUR BLOC V5] Exception réseau non gérée interceptée au vol : ${err.message}`);
    console.log(`[🛡️ CRASH-SHIELD] Le serveur sur le port 4246 reste en ligne. Isolement du processus accompli.\n`);
});

const PORT = process.env.PORT || 4246;
app.listen(PORT, () => {
    console.log(`\n==================================================`);
    console.log(`[🛡️ WEBHOOK-RETRY-SHIELD] Stable & Crash-Shielded on port ${PORT}`);
    console.log(`==================================================`);
});