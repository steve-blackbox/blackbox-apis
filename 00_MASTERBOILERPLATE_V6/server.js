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
// 🚀 ROUTAGE DIRECT : VAGUE 01 (ROBOTS 01 À 05)
// ==========================================

// Robot 01 : Code Shield Utility (Validateur & Obfuscateur Léger)
app.use('/v1/code-shield', require('./robots/robot01/index'));

// Robot 02 : Payload Compressor (Optimiseur de données d'API)
app.use('/v1/payload-compress', require('./robots/robot02/index'));

// Robot 03 : Audio Converter Master (Optimiseur de soute WAVE/MP3)
app.use('/v1/audio-convert', require('./robots/robot03/index'));

// Robot 04 : Meta Stripper Pro (Purgeur de métadonnées propres)
app.use('/v1/meta-stripper', require('./robots/robot04/index'));

// Robot 05 : JSON Flattener Ultra (Compresseur de structures)
app.use('/v1/json-flatten', require('./robots/robot05/index'));

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