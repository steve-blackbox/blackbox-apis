/**
 * 🛰️ BLACKBOX AUDIO LABS LLC — CENTRAL APIS GATEWAY
 * 🚀 ARCHITECTURE MONOLITHIQUE CLOUD-NATIVE V6 — ZERO-OPS EPHEMERE
 * 🔒 INJECTEURS STRIPE LIVE VERROUILLÉS AU COFFRE
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const Stripe = require('stripe');

// Initialize Express Engine
const app = express();
const PORT = process.env.PORT || 10000;

// Initialize Stripe Engine with Secure Environment Variables
const stripeSecretKey = process.env.STRIPE_SECRET_KEY || '';
const stripe = new Stripe(stripeSecretKey);

// ==========================================
// 🛡️ MIDDLEWARES GLOBAUX DE SOUTE
// ==========================================
app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Server Availability Indicator (The Root Badge)
app.get('/', (req, res) => {
    res.status(200).send('HELLO, WORLD! BLACKBOX AUDIO LABS IS LIVE TO THE PLANET.');
});

// ==========================================
// 🚀 ROUTAGE DIRECT CORRIGE (REMONTEE AU DOSSIER PARENT)
// ==========================================

// Robot 01 : Asset Shrink Pro
app.use('/v1/asset-shrink', require('../asset_shrink'));

// Robot 02 : Exif Cloak Utility
app.use('/v1/exif-cloak', require('../exif_cloak'));

// Robot 03 : Link Purge Master
app.use('/v1/link-purge', require('../link-purge'));

// Robot 04 : JSON Flatten Ultra
app.use('/v1/json-flatten', require('../json_flatten'));

// Robot 05 : SVG Strip Core
app.use('/v1/svg-strip', require('../svg_strip'));

// ==========================================
// 💸 TUNNEL DE CAPTURE COMMERCIALE STRIPE
// ==========================================
app.post('/v1/checkout/create-session', async (req, res) => {
    const { priceId, successUrl, cancelUrl } = req.body;
    
    try {
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
// ⚡ DEMARRAGE DU CORE UNIVERSEL
// ==========================================
app.listen(PORT, () => {
    console.log(`[⚙️ ENGINE ACTIVE] Constellation running flawlessly on Port ${PORT}`);
});