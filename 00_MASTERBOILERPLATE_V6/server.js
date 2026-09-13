/**
 * 🛰️ BLACKBOX AUDIO LABS LLC — CENTRAL APIS GATEWAY
 * 🚀 ARCHITECTURE MONOLITHIQUE CLOUD-NATIVE V19 — AUTOMATE D'ÉLITE
 * 📥 SYSTEME DE LIVRAISON COMMERCIALE DYNAMIQUE PAR E-MAIL (DOMAINE PRO VERIFIÉ)
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const Stripe = require('stripe');

const app = express();
const PORT = process.env.PORT || 10000;

// Configuration sécurisée des instances tierces
const getStripeInstance = () => {
    const secureKey = process.env.STRIPE_SECRET_KEY || '';
    if (!secureKey) throw new Error("Missing STRIPE_SECRET_KEY.");
    return new Stripe(secureKey);
};

app.use(cors({ origin: '*' }));

// Gestion étanche du format brut pour le Webhook
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
// 📥 INTERCEPTEUR DE WEBHOOKS & EMAIL ENGINE
// ==========================================
app.post('/v1/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET || '';
    let event;

    try {
        const stripe = getStripeInstance();
        event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
        console.error(`[❌ WEBHOOK ERROR] Verification echouee: ${err.message}`);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Interception du paiement réussi
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const customerEmail = session.customer_details ? session.customer_details.email : null;
        
        console.log(`[🏆 CASH REÇU] Paiement valide pour la session: ${session.id}`);

        if (customerEmail) {
            console.log(`[📧 EMAIL TRIGGER] Lancement du protocole Resend Pro pour : ${customerEmail}`);
            
            // Génération d'une clé API fictive et sécurisée pour le client
            const generatedApiKey = `bb_live_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;

            try {
                // Routage natif vers l'API Resend sécurisé via domaine vérifié
                const response = await fetch('https://resend.com', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        from: 'BlackBox Control <control@blackbox-apis.com>',
                        to: customerEmail,
                        subject: '🔴 BlackBox Infrastructure Access Granted — API Ecosystem',
                        html: `
                            <div style="background-color: #030712; color: #f3f4f6; font-family: monospace; padding: 40px; border: 1px solid #1f2937; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                                <h2 style="color: #3b82f6; border-bottom: 1px solid #1f2937; padding-bottom: 15px; margin-top: 0;">⚡ ACCESS GRANTED — INFRASTRUCTURE FLUX</h2>
                                <p>Félicitations, votre acquisition de licence commerciale a été validée avec succès par nos serveurs sécurisés aux États-Unis.</p>
                                <div style="background-color: #0b0f19; border: 1px solid #1f2937; padding: 20px; border-radius: 4px; margin: 25px 0;">
                                    <span style="color: #9ca3af; font-size: 11px; text-transform: uppercase; display: block; margin-bottom: 5px;">Votre Clé API Secrète (Live) :</span>
                                    <strong style="color: #10b981; font-size: 16px; word-break: break-all;">${generatedApiKey}</strong>
                                </div>
                                <p style="color: #9ca3af; font-size: 12px; line-height: 1.6;">Pour connecter votre infrastructure, passez ce jeton dans votre en-tête HTTP : <br><code style="color: #3b82f6;">Authorization: Bearer ${generatedApiKey}</code></p>
                                <hr style="border: 0; border-top: 1px solid #1f2937; margin: 30px 0;">
                                <footer style="font-size: 11px; color: rgba(156, 163, 175, 0.4);">
                                    © 2026 BlackBox Audio Labs LLC. Systems Sterile. USD Compliant.
                                </footer>
                            </div>
                        `
                    })
                });

                if (response.ok) {
                    console.log(`[🚀 EMAIL SUCCESS] Mail de livraison envoye proprement via control@blackbox-apis.com à : ${customerEmail}`);
                } else {
                    const errorText = await response.text();
                    console.error(`[❌ EMAIL FAILED] Erreur API Resend : ${errorText}`);
                }
            } catch (emailError) {
                console.error(`[❌ EMAIL FATAL ERROR] Impossible de contacter Resend: ${emailError.message}`);
            }
        } else {
            console.warn("[⚠️ EMAIL WARN] Aucun e-mail trouve dans la session Stripe.");
        }
    }

    res.status(200).json({ received: true });
});

app.listen(PORT, () => {
    console.log(`[⚙️ ENGINE ACTIVE] Monolithe V19 operationnel sur le port ${PORT}`);
});