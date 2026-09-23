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
const { recordSale, getStats, saveLicense, isValidLicense, getAllActiveLicenseKeys, deactivateLicensesByPaddleSubscription } = require('./lib/db');

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
async function sendLicenseActivationEmail({ email, name, licenseKey }) {
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

        try {
            saveLicense({
                licenseKey,
                email: customerEmail,
                plan: purchasedPlan,
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
            await sendLicenseActivationEmail({ email: customerEmail, name: customerName, licenseKey });
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
        if (revoked > 0 && global.activeLicenseKeys) {
            global.activeLicenseKeys = new Set(['BB-ADMIN-CORE-99', ...getAllActiveLicenseKeys()]);
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
global.activeLicenseKeys = new Set(['BB-ADMIN-CORE-99', ...getAllActiveLicenseKeys()]);
console.log(`🔑 ${global.activeLicenseKeys.size} licence(s) active(s) rechargée(s) depuis la base persistante.`);

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
    }
    return res.json({ success: valid });
});

app.post('/v1/checkout', async (req, res) => {
    if (!paddleClient) {
        return res.status(503).json({ error: 'Paddle non configuré côté serveur (PADDLE_API_KEY manquante).' });
    }

    try {
        const { plan, endpoint_target } = req.body;

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

        // Création de la transaction Paddle : Paddle renvoie une URL de paiement (checkout.url)
        // vers laquelle on redirige le client (ouverture de l'overlay Paddle.js côté front).
        const transaction = await paddleClient.transactions.create({
            items: [{ priceId: targetPriceId, quantity: 1 }],
            customData: {
                plan: planType || 'labs',
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

function requireLicense(req, res, next) {
    const authHeader = req.headers['authorization'] || '';
    const bearerToken = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : null;
    const token = bearerToken || req.body?.token;

    if (!token || !global.activeLicenseKeys.has(token)) {
        return res.status(401).json({ success: false, message: "» INGRESS REFUSED: Invalid or missing license key." });
    }
    next();
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
    app.use(`/v1/${robotName}`, requireLicense, require(`./${robotName}`));
});

// 🎛️ IGNITION DES RÉACTEURS SUR LE PORT CLOUD REGLÉ PAR RENDER
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`[🚀 SERVER LIVE]: Port ${PORT}`);
});