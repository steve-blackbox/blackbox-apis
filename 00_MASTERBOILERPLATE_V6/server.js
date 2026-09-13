/**
 * 🛰️ BLACKBOX AUDIO LABS LLC — CENTRAL APIS GATEWAY
 * 🚀 ARCHITECTURE MONOLITHIQUE CLOUD-NATIVE V10 — ZERO-OPS EPHEMERE
 * ⚡ WEBHOOKS STRIPE INTEGRÉS POUR LIVRAISON EN AUTO-PILOTE
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const Stripe = require('stripe');

const app = express();
const PORT = process.env.PORT || 10000;

// Dynamic Stripe Initializer helper
const getStripeInstance = () => {
    const secureKey = process.env.STRIPE_SECRET_KEY || '';
    if (!secureKey) throw new Error("Missing STRIPE_SECRET_KEY in Environment.");
    return new Stripe(secureKey);
};

// ==========================================
// 🛡️ MIDDLEWARES GLOBAUX DE SOUTE
// ==========================================
app.use(cors({ origin: '*' }));

// ⚠️ ATTENTION TEXT/RAW IMPÉRATIF POUR VALIDER LA SIGNATURE DES WEBHOOKS STRIPE
app.use((req, res, next) => {
    if (req.originalUrl === '/v1/webhook') {
        next();
    } else {
        express.json({ limit: '50mb' })(req, res, next);
    }
});
app.use((req, res, next) => {
    if (req.originalUrl !== '/v1/webhook') {
        express.urlencoded({ extended: true, limit: '50mb' })(req, res, next);
    } else {
        next();
    }
});

// 📦 CARROSSERIE VISUELLE BENTO LIÉE
app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (req, res) => {
    res.status(200).send('HEALTH CHECK: ACTIVE.');
});

// ==========================================
// 🚀 ROUTAGE APIS DIRECT (ROBOTS V1 & V3)
// ==========================================
app.use('/v1/asset-shrink', require('./asset_shrink'));
app.use('/v1/exif-cloak', require('./exif_cloak'));
try { app.use('/v1/link-purge', require('./link_purge')); } catch (e) { app.use('/v1/link-purge', require('./link-purge')); }
try { app.use('/v1/json-flatten', require('./json_flatten')); } catch (e) { app.use('/v1/json-flatten', require('./json-flatten')); }
try { app.use('/v1/svg-strip', require('./svg_strip')); } catch (e) { app.use('/v1/svg-strip', require('./svg-strip')); }

app.use('/v3/html-extractor', require('./html_extractor'));
app.use('/v3/text-tokenizer', require('./text_tokenizer'));
app.use('/v3/csv-dedupe', require('./csv_dedupe'));
app.use('/v3/yaml-json-converter', require('./yaml_json_converter'));
app.use('/v3/mock-generator', require('./mock_generator'));

// ==========================================
// 💸 TUNNEL DE CHECKOUT AUTOMATIQUE
// ==========================================
app.post('/v1/checkout/create-session', async (req, res) => {
    const { priceId, successUrl, cancelUrl } = req.body;
    try {
        const stripe = getStripeInstance();
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [{ price: priceId, quantity: 1 }],
            mode: 'payment',
            success_url: successUrl || 'https://blackbox-apis.com',
            cancel_url: cancelUrl || 'https://blackbox-apis.com',
        });
        res.status(200).json({ id: session.id, url: session.url });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// 📥 L'INJECTEUR INTERCEPTEUR DE WEBHOOKS
// ==========================================
app.post('/v1/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET || '';
    
    let event;
    try {
        const stripe = getStripeInstance();
        event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
        console.error(`[🚨 WEBHOOK INVALID SIGNATURE]`, err.message);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Interception magique du succès de facturation
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const clientEmail = session.customer_details.email;
        const totalPaid = session.amount_total / 100;
        
        console.log(`[🏆 CASH RECU] ${totalPaid} USD captes de la part de : ${clientEmail}`);
        
        // C'EST ICI QU'ON DÉCLENCHERA L'ENVOI AUTOMATIQUE PAR EMAIL DANS LE PROCHAIN SPRINT
        console.log(`[🚀 AUTOMATE] Generation et livraison du Token d'accès API en cours...`);
    }

    res.status(200).json({ received: true });
});

app.listen(PORT, () => {
    console.log(`[⚙️ ENGINE ACTIVE] Monolithe V10 en ligne sur le port ${PORT}`);
});