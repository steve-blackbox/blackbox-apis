/**
 * 🛰️ BLACKBOX AUDIO LABS LLC — CENTRAL APIS GATEWAY
 * 🚀 ARCHITECTURE MONOLITHIQUE CLOUD-NATIVE V8 — ZERO-OPS EPHEMERE
 * 🔒 INJECTEURS STRIPE LIVE VERROUILLÉS DYNAMIQUEMENT AU CLIC
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const Stripe = require('stripe');

// Initialize Express Engine
const app = express();
const PORT = process.env.PORT || 10000;

// ==========================================
// 🛡️ MIDDLEWARES GLOBAUX DE SOUTE
// ==========================================
app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// 📦 LIAISON DYNAMIQUE DE LA CARROSSERIE VISUELLE (DOSSIER PUBLIC)
app.use(express.static(path.join(__dirname, 'public')));

// Server Availability Indicator
app.get('/health', (req, res) => {
    res.status(200).send('HELLO, WORLD! BLACKBOX AUDIO LABS IS LIVE.');
});

// ==========================================
// 🚀 ROUTAGE DIRECT : VAGUE 01 (ROBOTS 01 À 05)
// ==========================================
app.use('/v1/asset-shrink', require('./asset_shrink'));
app.use('/v1/exif-cloak', require('./exif_cloak'));
try { app.use('/v1/link-purge', require('./link_purge')); } catch (e) { app.use('/v1/link-purge', require('./link-purge')); }
try { app.use('/v1/json-flatten', require('./json_flatten')); } catch (e) { app.use('/v1/json-flatten', require('./json-flatten')); }
try { app.use('/v1/svg-strip', require('./svg_strip')); } catch (e) { app.use('/v1/svg-strip', require('./svg-strip')); }

// ==========================================
// 🚀 ROUTAGE DIRECT : VAGUE 03 (ROBOTS 11 À 15)
// ==========================================
app.use('/v3/html-extractor', require('./html_extractor'));
app.use('/v3/text-tokenizer', require('./text_tokenizer'));
app.use('/v3/csv-dedupe', require('./csv_dedupe'));
app.use('/v3/yaml-json-converter', require('./yaml_json_converter'));
app.use('/v3/mock-generator', require('./mock_generator'));

// ==========================================
// 💸 TUNNEL DE CAPTURE COMMERCIALE STRIPE (DYNAMIC INITIALIZATION)
// ==========================================
app.post('/v1/checkout/create-session', async (req, res) => {
    const { priceId, successUrl, cancelUrl } = req.body;
    
    try {
        // 🔒 Extraction de la clé secrète en direct de la soute Render à la milliseconde
        const secureKey = process.env.STRIPE_SECRET_KEY || '';
        if (!secureKey) throw new Error("Stripe Private Key is empty in Render Dashboard Environment.");
        
        // Initialisation à chaud
        const stripe = new Stripe(secureKey);
        
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [{ price: priceId, quantity: 1 }],
            mode: 'payment',
            success_url: successUrl || 'https://blackbox-apis.com',
            cancel_url: cancelUrl || 'https://blackbox-apis.com',
        });
        
        res.status(200).json({ id: session.id, url: session.url });
    } catch (error) {
        console.error("[🚨 STRIPE CRASH]", error.message);
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// ⚡ DEMARRAGE DU CORE UNIVERSEL
// ==========================================
app.listen(PORT, () => {
    console.log(`[⚙️ ENGINE ACTIVE] Constellation running flawlessly on Port ${PORT}`);
});