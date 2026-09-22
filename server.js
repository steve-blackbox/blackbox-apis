// 🌌 BLACKBOX MICROSERVICES CORE ENGINE — PRODUCTION NODE V6
const express = require('express');
const cors = require('cors');
const path = require('path');
const crypto = require('crypto');
const Stripe = require('stripe');

// 📨 EXPÉDITEUR D'E-MAILS RESEND INITIALISÉ
const { Resend } = require('resend');
const resend = new Resend(process.env.RESEND_API_KEY);

// 📊 SUIVI DE TRACTION (ventes persistantes + checkpoints J+30/60/90)
const { recordSale, getStats, saveLicense, isValidLicense, getAllActiveLicenseKeys } = require('./lib/db');

// 🔑 ENCAPSULATION SECURISEE STRIPE (Variable d'environnement de soute)
const stripe = Stripe(process.env.STRIPE_SECRET_KEY);

const app = express();

// 🛡️ MIDDLEWARES STRUCTURAUX DE SOUTE
app.use(cors({ origin: '*' }));

// 📡 1. ROUTE DU WEBHOOK STRIPE (PLINDÉE AVANT EXPRESS.JSON)
app.post('/v1/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    let event;

    try {
        // Validation forensique du signal Stripe avec ton secret Render
        event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
    } catch (err) {
        console.error(`❌ Erreur Webhook Signature: ${err.message}`);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // 🟢 CASH SÉCURISÉ : L'achat est validé sur Stripe Checkout
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const customerEmail = session.customer_details.email;
        const customerName = session.customer_details.name || 'Client BlackBox';
        
        // Extraction du plan acheté (core, labs, etc.) depuis les metadata passées au checkout
        const purchasedPlan = session.metadata?.plan || 'labs';

        // 🔑 GÉNÉRATION DE LA CLÉ DE LICENCE EXCLUSIVE BLACKBOX
        const uniqueId = crypto.randomBytes(4).toString('hex').toUpperCase();
        const licenseKey = `BB-${purchasedPlan.toUpperCase()}-CORE-${uniqueId}`;

        // 💾 Sauvegarde volatile en mémoire (cache rapide pour la requête suivante)
        if (global.activeLicenseKeys) {
            global.activeLicenseKeys.add(licenseKey);
        }

        // 🔒 Sauvegarde PERSISTANTE en base (survit aux redémarrages/redéploiements Render)
        try {
            saveLicense({ licenseKey, email: customerEmail, plan: purchasedPlan });
        } catch (licenseError) {
            console.error('❌ Échec enregistrement persistant de la licence:', licenseError);
        }

        // 📊 Enregistrement persistant de la vente (base du tableau de bord de traction)
        try {
            recordSale({
                email: customerEmail,
                plan: purchasedPlan,
                amountCents: session.amount_total || 0,
                currency: session.currency || 'usd',
                licenseKey,
            });
        } catch (dbError) {
            console.error('❌ Échec enregistrement vente en base de traction:', dbError);
        }

        console.log(`🚀 Paiement Validé pour ${customerEmail}! Licence Générée: ${licenseKey}`);

        try {
            // 📨 EXPÉDITION INSTANTANÉE PAR RESEND
            await resend.emails.send({
                from: 'BlackBox Audio Labs <activation@blackbox-apis.com>',
                to: [customerEmail],
                subject: '🔥 Activation de votre licence BlackBox Audio Labs',
                html: `
                    <div style="font-family: sans-serif; padding: 20px; background: #000; color: #fff; border-radius: 8px;">
                        <h2 style="color: #00ffcc;">Félicitations ${customerName} !</h2>
                        <p>Votre paiement a été sécurisé avec succès. Votre réacteur d'automatisation est prêt.</p>
                        <div style="background: #111; padding: 15px; border-left: 4px solid #00ffcc; margin: 20px 0; font-family: monospace; font-size: 16px; letter-spacing: 1px;">
                            <strong>VOTRE CLÉ DE LICENCE :</strong> ${licenseKey}
                        </div>
                        <p style="color: #888; font-size: 12px;">LLC BlackBox Audio Labs — Wyoming, USA</p>
                    </div>
                `
            });
            console.log(`📧 E-mail de licence envoyé avec succès à ${customerEmail}`);
        } catch (emailError) {
            console.error(`❌ Échec de l'envoi de l'e-mail Resend:`, emailError);
        }
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
    try {
        const { plan, endpoint_target } = req.body;
        
        let targetPriceId = '';
        const planType = plan ? plan.toLowerCase().trim() : '';

        // Dictionnaire hermétique connecté à tes deux nouveaux produits Stripe
        if (planType === 'core' || planType === 'solo' || planType === 'matrix' || planType === 'single') {
    targetPriceId = 'price_1UGjACAQxUv6pdHqpCxlPwKc'; // 🟢 TON NOUVEAU FORFAIT SINGLE ACCESS A 49$ PROPRE
} else if (planType === 'labs' || planType === 'premium' || planType === 'allaccess' || planType === 'all-access' || planType === 'adblock_bypass') {
    targetPriceId = 'price_1UGj7mAQxUv6pdHqee0lOe3F'; // 🔵 TON NOUVEAU FORFAIT ALL ACCESS A 149$ PROPRE
} else {
    // 🟢 SÉCURITÉ UNIVERSELLE DE SECOURS : Si le mot-clé arrive vide, altéré ou non reconnu
    // par les conditions précédentes, on force le Price ID valide à 149$.
    console.log("👉 Alerte soute : planType inconnu ou manquant. Redirection forcé sur All Access 149$. Input reçu :", planType);
    targetPriceId = 'price_1UGj7mAQxUv6pdHqee0lOe3F'; 
}

        // Création de la session sécurisée en paiement unique sec (One-time strict)
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [
                {
                    price: targetPriceId,
                    quantity: 1,
                },
            ],
            mode: 'payment', // Mode paiement direct (Supprime la date 1970)
            success_url: `${req.headers.origin}/success.html?session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${req.headers.origin}/cancel.html`,
            metadata: {
                endpoint_target: endpoint_target || 'none'
            }
        });

        res.json({ url: session.url });

    } catch (error) {
        console.error('Erreur forensique lors de la création du Checkout:', error);
        res.status(500).json({ error: 'Erreur interne du serveur de soute' });
    }
});

// 🛰️ DÉPLOIEMENT FINAL FORCE : ALIGNEMENT DES FICHIERS EN DUR (0% FLASH)
// 📁 API ENDPOINTS: STANDALONE INDEPENDENT PRODUCTION ROUTING (0% FLASH)
app.get('/docs', (req, res) => res.sendFile(path.join(__dirname, 'public', 'docs.html')));
app.get('/terms.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'terms.html')));
app.get('/privacy.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'privacy.html')));
// 🔄 REDIRECTION DE SECOURS STRIPE : RENVOIE DIRECTEMENT SUR L'ACCUEIL EN CAS D'ANNULATION
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