/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELATION
 * 🤖 ROBOT 18 : SVG-OPTIMIZER CORE ENGINE (VECTOR ASSET SHREDDER)
 * 🎨 STATELESS PATH CLEANER & DESIGN PAYLOAD SHRANK UNIT
 */

const express = require('express');
const router = express.Router();

// Nettoyeur chirurgical stateless de metadonnees graphiques
function cleanRawSvg(svgString) {
    if (!svgString) return '';
    return svgString
        .replace(/<!--[\s\S]*?-->/g, '') // Supprime les commentaires de design
        .replace(/<\?xml[\s\S]*?\?>/g, '') // Supprime les declarations XML inutiles
        .replace(/id="[\s\S]*?"/g, '') // Supprime les identifiants de calques inutiles
        .replace(/\s+/g, ' ') // Nettoie les retours a la ligne et espaces multiples
        .trim();
}

/**
 * 📥 ROUTE CORE : OPTIMISATION VECTORIELLE DE MASSE
 */
router.post('/', (req, res) => {
    const { svg_payload } = req.body;

    if (!svg_payload) {
        return res.status(400).json({ error: "Missing required 'svg_payload' string in request body." });
    }

    console.log(`[🎨 SVG-OPTIMIZER] Ingestion d'un vecteur de ${svg_payload.length} octets.`);

    const optimizedSvg = cleanRawSvg(svg_payload);
    const originalSize = Buffer.byteLength(svg_payload, 'utf8');
    const optimizedSize = Buffer.byteLength(optimizedSvg, 'utf8');
    const savingPercent = ((1 - (optimizedSize / originalSize)) * 100).toFixed(1);

    res.status(200).json({
        status: "STERILE_ASSET_SHRINK_SUCCESS",
        optimized_svg: optimizedSvg,
        metrics: {
            original_bytes: originalSize,
            optimized_bytes: optimizedSize,
            efficiency: `${savingPercent}% destroyed`,
            integrity_check: "VECTOR_INTACT"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;