/**
 * 🛰️ BLACKBOX AUDIO LABS LLC — CENTRAL APIS GATEWAY
 * 🚀 ARCHITECTURE MONOLITHIQUE CLOUD-NATIVE V12 — ZERO-OPS EPHEMERE
 * 💎 UNIFORMISATION TOTALE DES 5 ROBOTS APPARENTS V1
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const Stripe = require('stripe');

const app = express();
const PORT = process.env.PORT || 10000;

const getStripeInstance = () => {
    const secureKey = process.env.STRIPE_SECRET_KEY || '';
    if (!secureKey) throw new Error("Missing STRIPE_SECRET_KEY.");
    return new Stripe(secureKey);
};

app.use(cors({ origin: '*' }));

app.use((req, res, next) => {
    if (req.originalUrl === '/v1/webhook') next();
    else express.json({ limit: '50mb' })(req, res, next);
});
app.use((req, res, next) => {
    if (req.originalUrl !== '/v1/webhook') express.urlencoded({ extended: true, limit: '50mb' })(req, res, next);
    else next();
});

app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (req, res) => { res.status(200).send('HEALTH: ACTIVE.'); });

// ==========================================
// 🚀 ROUTAGE APIS APPARENT MONOLITHE V1
// ==========================================
app.use('/v1/form-shield', require('./form_shield'));
app.use('/v1/audio-convert', require('./audio_convert'));
app.use('/v1/link-purge', require('./link_purge'));
app.use('/v1/json-flatten', require('./json_flatten'));
app.use('/v1/svg-strip', require('./svg_strip'));

// ==========================================
// 💸 TUNNEL DE CAPTURE COMMERCIALE STRIPE
// ==========================================
app.post('/v1/checkout/create-session', async (req, res) => {
    const { priceId, successUrl, cancelUrl } = req.body;
    try {
        const stripe = getStripeInstance();
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [{ price: priceId, quantity: 1 }],
            mode: 'payment',
            success_url: successUrl,
            cancel_url: cancelUrl,
        });
        res.status(200).json({ id: session.id, url: session.url });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// 📥 INTERCEPTEUR DE WEBHOOKS
// ==========================================
app.post('/v1/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET || '';
    let event;
    try {
        const stripe = getStripeInstance();
        event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }
    if (event.type === 'checkout.session.completed') {
        console.log(`[🏆 CASH RECU] Webhook synchronisé.`);
    }
    res.status(200).json({ received: true });
});

app.listen(PORT, () => {
    console.log(`[⚙️ ENGINE ACTIVE] Monolithe V12 operationnel sur le port ${PORT}`);
});
