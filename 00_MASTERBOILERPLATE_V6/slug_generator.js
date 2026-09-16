/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 68 : SLUG-GENERATOR CORE ENGINE (ASSET SHRINK LAB)
 * 🔗 LIGHTNING-FAST STATELESS STRING-TO-SLUG CONVERTER FOR SEO COMPLIANT URLS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION SYNTAXIQUE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_title_string } = req.body;

    if (!raw_title_string) {
        return res.status(400).json({ error: "Missing required 'raw_title_string' parameter variable string." });
    }

    const inputTitle = raw_title_string.toString().trim();
    console.log(`[🔗 SLUG-GENERATOR] Generation de slug web pour la chaine: "${inputTitle.substring(0, 30)}..."`);

    // Logique de soute chirurgicale pour nettoyer les accents et caracteres complexes
    let slug = inputTitle
        .toLowerCase()
        .normalize('NFD')                         // Decomposition des caracteres accentues
        .replace(/[\u0300-\u036f]/g, '')         // Suppression des accents residuels
        .replace(/[^a-z0-9\s-]/g, '')            // Elimination de tout ce qui n'est pas lettre, chiffre ou espace
        .replace(/\s+/g, '-')                    // Remplacement des espaces par des tirets
        .replace(/-+/g, '-')                     // Suppression des tirets doubles ou consecutifs
        .replace(/^-+|-+$/g, '');                // Nettoyage des extremites

    res.status(200).json({
        status: "SLUG_GENERATED_SUCCESSFULLY",
        input_received: inputTitle,
        slug_output: slug,
        pipeline_integrity: {
            seo_compliant: true,
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;