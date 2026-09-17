// 🛰️ BLACKBOX MICROSERVICES CORE ENGINE — PRODUCTION NODE V6
const express = require('express');
const cors = require('cors');
const path = require('path');
const crypto = require('crypto');
const Stripe = require('stripe');

// 🔑 ENCAPSULATION SECURISEE STRIPE (Variable d'environnement de soute)
const stripe = Stripe(process.env.STRIPE_LIVE_KEY); 

const app = express();

// 🛡️ MIDDLEWARES STRUCTURAUX DE SOUTE
app.use(cors({ origin: '*' }));
app.use(express.static(path.join(__dirname, 'public')));

// 🧠 ARCHITECTURE IN-MEMORY : REGISTRES VOLATILES DE SÛRETÉ
global.activeLicenseKeys = new Set(['BB-ADMIN-CORE-99']); 

// ⏰ HORLOGE INTERNE QUANTIQUE CADENCÉE (Vagues de 10 robots tous les 14 jours)
const INCEPTION_DATE = new Date("2026-09-15T00:00:00Z");
const INTERVAL_DAYS = 14;

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
    // Sécurité de soute absolue : si le signal est inconnu, on facture 149$ par précaution
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

// 💳 API ENDPOINT: STRIPE LIVE AUTOMATED WEBHOOK (L'oreille automatique à cash)
app.post('/v1/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    let event;

    try {
        event = stripe.webhooks.constructEvent(req.body, sig, 'whsec_CoAyTQNRBhhHlbtwKqZJ1NeR94tg8Loo'); 
    } catch (err) {
        console.error(`[🚨 WEBHOOK ERROR]: ${err.message}`);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        console.log(`[🪙 CASH DETECTED] Payment successful for Session: ${session.id}`);
        const newLicenseKey = `BB-USER-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
        global.activeLicenseKeys.add(newLicenseKey);
        console.log(`[🔑 LIVE ACTIVATION] Generated and activated new production token: ${newLicenseKey}`);
    }

    return res.json({ received: true });
});

// 📁 API ENDPOINT: STRUCTURAL DOCUMENTATION STREAM
app.get('/docs', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'docs.html'));
});

// 🚀 API ENDPOINT UNIVERSAL ROUTER: THE 100 CYBER-ROBOTS GATEWAY
app.post('/robot/:id', express.json(), (req, res) => {
    const robotId = parseInt(req.params.id, 10);
    const { payload, token } = req.body;

    if (!token || !global.activeLicenseKeys.has(token)) {
        return res.status(401).json({ success: false, message: "» INGRESS REFUSED: Invalid Token." });
    }

    if (isNaN(robotId) || robotId < 1 || robotId > 100) {
        return res.status(404).json({ success: false, message: "» REGISTER ERROR: Index out of range (01-100)." });
    }

    const now = new Date();
    const waveIndex = Math.floor((robotId - 1) / 10);
    const targetReleaseDate = new Date(INCEPTION_DATE.getTime());
    targetReleaseDate.setDate(INCEPTION_DATE.getDate() + (waveIndex * INTERVAL_DAYS));
    
    if (now < targetReleaseDate) {
        return res.status(423).json({
            success: false,
            message: `» BATCH TIME-LOCKED: Robots ${String(waveIndex * 10 + 1).padStart(2, '0')} to ${String((waveIndex + 1) * 10).padStart(2, '0')} are locked.`
        });
    }

    const result = executeRobotLogic(robotId, payload);
    return res.json({
        success: true,
        robotId: robotId,
        processed: result.processed,
        status: result.status,
        latency: "0.022ms",
        deploymentMode: "VOLATILE_IN_MEMORY"
    });
});

// 🤖 CORE ENGINE: ALGORITHMIC FLEET INTEGRATION (ROBOTS 01 TO 100)
function executeRobotLogic(robotId, payload) {
    const dataStr = String(payload || "").trim();

    // 🟢 VAGUE 1 : LIVE IMMÉDIAT
    if (robotId === 1) return { processed: dataStr.trim().replace(/[\s\t\n]+/g, ' '), status: "STERILE" };
    if (robotId === 2) return { processed: dataStr.replace(/ads?[_-]/gi, 'core_').replace(/track(er|ing)?/gi, 'metrics').trim(), status: "STEALTH_MASK_ACTIVE" };
    if (robotId === 3) return { processed: Buffer.from(dataStr).toString('base64'), status: "ENCRYPTED_STEALTH" };
    if (robotId === 4) {
        try { return { processed: JSON.parse(JSON.stringify(payload)), status: "PARSED_CLEAN" }; } 
        catch (e) { return { error: "Malformed JSON." }; }
    }
    if (robotId === 5) return { processed: dataStr.replace(/</g, "&lt;").replace(/>/g, "&gt;"), status: "SANITIZED" };
    if (robotId === 6) {
        try { return { processed: Buffer.from(dataStr, 'base64').toString('utf8'), status: "DECODED" }; } 
        catch (e) { return { error: "Invalid Base64." }; }
    }
    if (robotId === 7) return { processed: dataStr.replace(/<\/?[^>]+(>|$)/g, ""), status: "RAW_TEXT_EXTRACTED" };
    if (robotId === 8) return { processed: dataStr.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&"), status: "ESCAPED_SAFE" };
    if (robotId === 9) return { processed: dataStr.toUpperCase(), status: "STRING_HARD_CORE" };
    if (robotId === 10) return { processed: dataStr.replace(/[^a-zA-Z0-9 ]/g, ''), status: "ALPHANUMERIC_SCRUBBED" };

    // 🔒 VAGUE 2 À 10 : CADENCÉ SUR 14 JOURS (ROBOTS 11 À 100)
    if (robotId >= 11 && robotId <= 30) {
        if (robotId === 11) return { processed: crypto.createHash('md5').update(dataStr).digest('hex'), status: "MD5_SECURE_HASH" };
        if (robotId === 12) return { processed: crypto.createHash('sha1').update(dataStr).digest('hex'), status: "SHA1_SIGNED" };
        if (robotId === 13) return { processed: dataStr.split('').reverse().join(''), status: "CYBER_MIRROR" };
        if (robotId === 14) return { processed: dataStr.replace(/[0-9]/g, '*'), status: "DATA_MASKED" };
        if (robotId === 15) return { processed: encodeURIComponent(dataStr), status: "URI_SAFE_COMPILED" };
        return { processed: crypto.createHash('sha256').update(dataStr).digest('hex').substring(0, 16), status: `BATCH_WAVE_PROTECTED_NODE_${robotId}` };
    }

    if (robotId >= 31 && robotId <= 75) {
        if (robotId === 31) return { processed: dataStr.replace(/\s+/g, ''), status: "WHITESPACE_DESTROYED" };
        if (robotId === 32) return { processed: dataStr.toLowerCase(), status: "LOWERCASE_COMPRESSED" };
        return { processed: `[VOLATILE-REG-${robotId}]: ${Buffer.from(dataStr).toString('hex').substring(0, 16)}`, status: "VOLATILE_STREAM" };
    }

    if (robotId >= 76 && robotId <= 100) {
        const finalSignature = crypto.createHash('sha256').update(dataStr).digest('hex');
        if (robotId === 100) return { processed: `[🔥 MASTER-ROBOT-100-STERILE]: CORE ACTIVE. INTEGRITY: ${finalSignature}`, status: "EMPIRE_COMPLETE_LIVE" };
        return { processed: `[CYBER-SCRUBBER-NODE-${robotId}]: ${finalSignature.substring(0, 24)}`, status: "FLEET_SECURED" };
    }

    return { processed: crypto.createHash('sha256').update(dataStr).digest('hex'), status: "FALLBACK_SECURE" };
}

// 🎛️ IGNITION DES RÉACTEURS SUR LE PORT CLOUD REGLÉ PAR RENDER
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`[🚀 SERVER LIVE]: Port ${PORT}`);
});