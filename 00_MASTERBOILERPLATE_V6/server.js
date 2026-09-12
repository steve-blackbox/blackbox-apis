const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// ⚙️ IMPORTS DES MOTEURS CLOUD-NATIVE VAGUE 02
const { cleanAndMinifySVG } = require('./svg_strip');
const { flattenObject } = require('./json_flatten');

// Middlewares d'analyse globaux (Sauf pour les Webhooks Stripe bruts)
app.use((req, res, next) => {
    if (req.originalUrl === '/api/webhook/stripe') {
        next();
    } else {
        express.json()(req, res, next);
    }
});

// 🌐 ROUTE DE CONTRÔLE DE SANTÉ DE SÔUTE
app.get('/api/health', (req, res) => {
    res.status(200).json({ status: 'OK', message: 'Hangar operational.' });
});

// 💳 LE RÉACTEUR D'INTERCEPTION STRIPE (Déclenché post-achat par le client)
app.post('/api/webhook/stripe', express.raw({ type: 'application/json' }), (req, res) => {
    let event = req.body;

    // Structure d'isolation de l'événement d'achat réussi
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const customerEmail = session.customer_details.email;
        const tier = session.metadata.tier || 'solo';

        console.log(`[& CASH_IN] Payment confirmed for ${customerEmail} - Tier: ${tier.toUpperCase()}`);

        // Logique de routage éphémère en mémoire vive vers la page de délivrance
        // Aucun enregistrement en base SQL - Zéro stockage de logs clients
        return res.status(200).json({
            success: true,
            redirect: `/download?token=${Buffer.from(customerEmail).toString('base64')}&tier=${tier}`
        });
    }

    res.status(200).json({ received: true });
});

// 🛰️ ROUTE API CLOUD-NATIVE ROBOT 09 (SVG-STRIP)
app.post('/api/v1/svg-strip', (req, res) => {
    const { svg } = req.body;
    
    if (!svg) {
        return res.status(400).json({ error: 'Soute vide. SVG requis.' });
    }

    try {
        const cleanedSVG = cleanAndMinifySVG(svg);
        return res.json({
            success: true,
            robot: '09_svg_strip',
            originalSize: svg.length,
            cleanedSize: cleanedSVG.length,
            savedBytes: svg.length - cleanedSVG.length,
            data: cleanedSVG
        });
    } catch (error) {
        return res.status(500).json({ error: 'Friture dans le traitement XML du serveur.' });
    }
});

// 🛰️ ROUTE API CLOUD-NATIVE ROBOT 10 (JSON-FLATTEN)
app.post('/api/v1/json-flatten', (req, res) => {
    const { data } = req.body;
    
    if (!data || typeof data !== 'object') {
        return res.status(400).json({ error: 'Soute vide ou format JSON invalide.' });
    }

    try {
        const flattened = flattenObject(data);
        return res.json({
            success: true,
            robot: '10_json_flatten',
            isFlattened: true,
            originalKeysCount: Object.keys(data).length,
            flattenedKeysCount: Object.keys(flattened).length,
            data: flattened
        });
    } catch (error) {
        return res.status(500).json({ error: 'Friture dans le traitement du payload JSON.' });
    }
});

// =========================================================================
// // RUNTIME ACTIVATION HOOK (DÉMARRAGE DU RÉACTEUR)
// =========================================================================

app.use((req, res) => {
    res.status(404).json({ error: "RESOURCE_NOT_FOUND", message: "Sterile node isolation active." });
});

app.listen(PORT, () => {
    console.log("=================================================================");
    console.log(`[🚀 LAUNCH] 00_MASTERBOILERPLATE_V6 deployed successfully.`);
    console.log(`[🛰️ ROUTER] Running locally on: http://localhost:${PORT}`);
    console.log(`[🔒 SECURITY] Ready for Escalier Launch sequence deployment.`);
    console.log("=================================================================");
});