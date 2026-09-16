/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 31 : HTML-MINIFY CORE ENGINE (COMPACT DOM SHREDDER)
 * ⚡ LIGHTNING-FAST CORES TO COMPRESS AND COLLAPSE BLATED WEB PAGES
 */

const express = require('express');
const router = express.Router();

// Fonction clinique de minification HTML de soute (Stateless Compressor)
function cleanAndMinifyHtml(rawHtml) {
    if (!rawHtml) return '';
    return rawHtml
        .replace(/<!--[\s\S]*?-->/g, '') // Supprime tous les commentaires HTML
        .replace(/\s+/g, ' ') // Efface les espaces multiples, sauts de ligne et tabulations
        .replace(/>\s+</g, '><') // Supprime les espaces inutiles entre les balises DOM
        .trim();
}

/**
 * 📥 ROUTE CORE : COMPRESSION CHIRURGICALE HTML
 */
router.post('/', (req, res) => {
    const { html } = req.body;

    if (!html) {
        return res.status(400).json({ error: "Missing required 'html' string payload in request body." });
    }

    console.log(`[⚡ HTML-MINIFY] Compression de code en cours pour un flux de ${html.length} octets.`);

    const minifiedOutput = cleanAndMinifyHtml(html);
    const originalBytes = Buffer.byteLength(html, 'utf8');
    const minifiedBytes = Buffer.byteLength(minifiedOutput, 'utf8');
    const efficiency = ((1 - (minifiedBytes / originalBytes)) * 100).toFixed(2);

    res.status(200).json({
        status: "STERILE_HTML_MINIFIER_SUCCESS",
        minified_html: minifiedOutput,
        metrics: {
            original_size_bytes: originalBytes,
            minified_size_bytes: minifiedBytes,
            compression_ratio: `${efficiency}% saved`,
            rendering_impact: "HYPER_OPTIMAL"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;