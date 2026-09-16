/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 25 : UTM-BUILDER CORE ENGINE (TRACKING ATTRIBUTION SANITIZER)
 * 🎛️ AUTOMATED STRING REGEX UNIFIER FOR CLEAN MARKETING CAMPAIGN METRICS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : SÉGMENTATION ET PURGE DES CHAINES DE PARAMÈTRES MALFORMÉES
 */
router.post('/', (req, res) => {
    const { base_url, source, medium, campaign } = req.body;

    if (!base_url || !source) {
        return res.status(400).json({ error: "Missing required 'base_url' or 'source' parameter tags." });
    }

    console.log(`[🎛️ UTM-BUILDER] Alignement analytique de la chaine publicitaire pour : ${source}`);

    // Nettoyage agressif de soute : Forçage en minuscules et encodage URI conforme
    const safeSource = encodeURIComponent(source.toLowerCase().trim());
    const safeMedium = medium ? encodeURIComponent(medium.toLowerCase().trim()) : 'cpc';
    const safeCampaign = campaign ? encodeURIComponent(campaign.toLowerCase().trim()) : 'blackbox_fleet';

    // Verification des slashs de structure
    const cleanedBaseUrl = base_url.endsWith('/') ? base_url : `${base_url}/`;
    const finalUrl = `${cleanedBaseUrl}?utm_source=${safeSource}&utm_medium=${safeMedium}&utm_campaign=${safeCampaign}`;

    res.status(200).json({
        status: "ATTRIBUTION_STRING_SANITIZED",
        clean_url: finalUrl,
        components: {
            origin: base_url,
            utm_source: safeSource,
            utm_medium: safeMedium,
            utm_campaign: safeCampaign
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;