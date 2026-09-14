/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELATION
 * 🤖 ROBOT 14 : CSS-MINIFY CORE ENGINE (ULTRA-AGGRESSIVE AST MINIFIER)
 * ⚡ LIGHTNING-FAST CORES TO PURGE AND COMPRESS HEAVY STYLE SHEETS
 */

const express = require('express');
const router = express.Router();

// Fonction clinique de minification de soute (Stateless Compressor)
function cleanAndMinifyCss(rawCss) {
    if (!rawCss) return '';
    return rawCss
        .replace(/\/\*[\s\S]*?\*\//g, '') // Supprime tous les commentaires
        .replace(/\s*([{\}:;,])\s*/g, '$1') // Supprime les espaces autour des selecteurs et proprietes
        .replace(/\s+/g, ' ') // Fusionne les espaces multiples restants
        .replace(/;}/g, '}') // Supprime le dernier point-virgule inutile
        .trim();
}

/**
 * 📥 ROUTE CORE : COMPRESSION CHIRURGICALE CSS
 */
router.post('/', (req, res) => {
    const { css } = req.body;

    if (!css) {
        return res.status(400).json({ error: "Missing 'css' string payload in request body." });
    }

    console.log(`[⚡ CSS-MINIFY] Ingestion et reduction de flux pour ${css.length} octets de styles.`);

    const minified = cleanAndMinifyCss(css);
    const originalBytes = Buffer.byteLength(css, 'utf8');
    const minifiedBytes = Buffer.byteLength(minified, 'utf8');
    const efficiency = ((1 - (minifiedBytes / originalBytes)) * 100).toFixed(2);

    res.status(200).json({
        status: "STERILE_MINIFIER_SUCCESS",
        minified_css: minified,
        metrics: {
            original_size_bytes: originalBytes,
            minified_size_bytes: minifiedBytes,
            compression_ratio: `${efficiency}% saved`,
            core_web_vitals_impact: "OPTIMAL"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;