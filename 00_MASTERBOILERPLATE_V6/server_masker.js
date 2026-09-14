/**
 * 🛰️ BLACKBOX AUDIO LABS LLC — CENTRAL APIS GATEWAY
 * 🚀 ARCHITECTURE MONOLITHIQUE CLOUD-NATIVE V34 — AUTOMATE SOUVERAIN
 * 📥 ALIGNEMENT EN PRODUCTION DES COMPOSANTS LOGIQUES DES VAGUES 01 À 11 CUMULÉES
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const Stripe = require('stripe');

const app = express();
const PORT = process.env.PORT || 10000;

// Configuration sécurisée des instances Stripe Live en production
const getStripeInstance = () => {
    const secureKey = process.env.STRIPE_SECRET_KEY || '';
    if (!secureKey) throw new Error("Missing STRIPE_SECRET_KEY inside process env execution layers.");
    return new Stripe(secureKey);
};

// Activation du filtrage Cross-Origin mondial
app.use(cors({ origin: '*' }));

// Gestion étanche du format brut indispensable pour l'intercepteur de Webhooks Stripe
app.use((req, res, next) => {
    if (req.originalUrl === '/v1/webhook') next();
    else express.json({ limit: '50mb' })(req, res, next);
});
app.use((req, res, next) => {
    if (req.originalUrl !== '/v1/webhook') express.urlencoded({ extended: true, limit: '50mb' })(req, res, next);
    else next();
});

// Distribution de la vitrine Bento commerciale statique re-soudée
app.use(express.static(path.join(__dirname, 'public')));

// Point de contrôle de vie réseau
app.get('/health', (req, res) => { res.status(200).send('HEALTH: ACTIVE. SYSTEMS STERILE.'); });

// ========================================================
// 🛡️ BRANCHEMENT DES APIS SOUVERAINS DE LA VAGUE 01 (LIVE)
// ========================================================
app.use('/v1/form-shield', require('./form_shield'));
app.use('/v1/audio-convert', require('./audio_convert'));
app.use('/v1/link-purge', require('./link_purge'));
app.use('/v1/json-flatten', require('./json_flatten'));
app.use('/v1/svg-strip', require('./svg_strip'));

// ========================================================
// ⚔️ RACCORDEMENT INDUSTRIEL DE LA VAGUE 02 (LIVE)
// ========================================================
app.use('/v1/ip-geolock', require('./ip_geolock'));
app.use('/v1/md-parser', require('./md_parser'));
app.use('/v1/scheduler-shield', require('./scheduler_shield'));
app.use('/v1/css-minify', require('./css_minify'));
app.use('/v1/agent-detect', require('./agent_detect'));

// ========================================================
// 💣 ARMEMENT ET ACTIVATION DU CENTRAL DE LA VAGUE 03 (LIVE)
// ========================================================
app.use('/v1/json-validate', require('./json_validate'));
app.use('/v1/proxy-wrap', require('./proxy_wrap'));
app.use('/v1/svg-optimizer', require('./svg_optimizer'));
app.use('/v1/uptime-check', require('./uptime_check'));
app.use('/v1/log-sanitizer', require('./log_sanitizer'));
// ========================================================
// 📈 ARMEMENT ET EXPULSION DE LA VAGUE 04 MARKETING (LIVE)
// ========================================================
app.use('/v1/adblock-bypass', require('./adblock_bypass'));
app.use('/v1/link-rotator', require('./link_rotator'));
app.use('/v1/metadata-scraper', require('./metadata_scraper'));
app.use('/v1/schema-gen', require('./schema_gen'));
app.use('/v1/utm-builder', require('./utm_builder'));

// ========================================================
// 💳 ACCROCHAGE DE LA VAGUE 05 FINTECH & DOCUMENTS (LIVE)
// ========================================================
app.use('/v1/currency-live', require('./currency_live'));
app.use('/v1/vat-validator', require('./vat_validator'));
app.use('/v1/pdf-flatten', require('./pdf_flatten'));
app.use('/v1/csv-parser', require('./csv_parser'));
app.use('/v1/tax-router', require('./tax_router'));

// ========================================================
// 🪓 INJECTION FRONT DE LA VAGUE 06 CYBER & CODE (LIVE)
// ========================================================
app.use('/v1/html-minify', require('./html_minify'));
app.use('/v1/text-extractor', require('./text_extractor'));
app.use('/v1/bot-detector', require('./bot_detector'));
app.use('/v1/cors-proxy', require('./cors_proxy'));
app.use('/v1/base64-converter', require('./base64_converter'));

// ========================================================
// 🪙 CONSTELLATION ACTIVE DE LA VAGUE 07 CRYPTO & SEO (LIVE)
// ========================================================
app.use('/v1/crypto-verify', require('./crypto_verify'));
app.use('/v1/sitemap-scraper', require('./sitemap_scraper'));
app.use('/v1/redirect-check', require('./redirect_check'));
app.use('/v1/json-ld-validator', require('./json_ld_validator'));
app.use('/v1/wei-converter', require('./wei_converter'));

// ========================================================
// 🛡️ ARMEMENT DE LA VAGUE 08 HEAVY REGEX LAB (LIVE)
// ========================================================
app.use('/v1/email-extractor', require('./email_extractor'));
app.use('/v1/phone-sanitizer', require('./phone_sanitizer'));
app.use('/v1/pii-masker', require('./pii_masker'));
app.use('/v1/ip-mask-validator', require('./ip_mask_validator'));

// ========================================================
// 📊 RACCORDEMENT CENTRAL DE LA VAGUE 09 (LIVE)
// ========================================================
app.use('/v1/mock-generator', require('./mock_generator'));
app.use('/v1/yaml-json-converter', require('./yaml_json_converter'));
app.use('/v1/html-extractor', require('./html_extractor'));
app.use('/v1/exif-cloak', require('./exif_cloak'));
app.use('/v1/header-inspector', require('./header_inspector'));

// ========================================================
// 🔀 RACCORDEMENT CENTRAL DE LA VAGUE 10 (LIVE)
// ========================================================
app.use('/v1/event-dispatcher', require('./event_dispatcher'));
app.use('/v1/event-filter', require('./event_filter'));
app.use('/v1/event-transformer', require('./event_transformer'));
app.use('/v1/link-signer', require('./link_signer'));
app.use('/v1/link-validator', require('./link_validator'));

// ========================================================
// 🎭 RACCORDEMENT CENTRAL DE LA VAGUE 11 (NEW LIVE)
// ========================================================
app.use('/v1/server-masker', require('./server_masker'));                 // Robot 56 branché !
app.use('/v1/cookie-signer', require('./cookie_signer'));                 // Robot 57 branché !
app.use('/v1/frame-guard', require('./frame_guard'));                     // Robot 58 branché !
app.use('/v1/content-type-enforcer', require('./content_type_enforcer')); // Robot 59 branché !
app.use('/v1/referrer-policy-cleaner', require('./referrer_policy_cleaner')); // Robot 60 branché ! Le soixantième !
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

    // Interception chirurgicale du paiement réussi pour délivrer le jeton client
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const customerEmail = session.customer_details ? session.customer_details.email : null;
        
        console.log(`[🏆 CASH REÇU] Paiement valide pour la session: ${session.id}`);

        if (customerEmail) {
            console.log(`[📧 EMAIL TRIGGER] Lancement du protocole Resend Pro pour : ${customerEmail}`);
            
            // Génération d'une clé API cryptographique fictive sécurisée pour l'accès client
            const generatedApiKey = `bb_live_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;

            try {
                // Routage natif vers l'API d'infrastructure Resend sécurisé
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
                    console.log(`[🚀 EMAIL SUCCESS] Mail de livraison envoye proprement à : ${customerEmail}`);
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

// Allumage et écoute du port applicatif par défaut sur le serveur
app.listen(PORT, () => {
    console.log(`[⚙️ ENGINE ACTIVE] Monolithe V34 operationnel sur le port ${PORT}`);
});