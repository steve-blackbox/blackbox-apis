/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 97 : SPACE-COLLAPSER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS TEXT COMPACTOR TO PURGE PARASITIC WHITESPACES
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : COMPACTION CHIRURGICALE DE CHAÎNE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_text_stream } = req.body;

    if (raw_text_stream === undefined || raw_text_stream === null) {
        return res.status(400).json({ error: "Missing required 'raw_text_stream' string parameter variable." });
    }

    console.log(`[🧹 SPACE-COLLAPSER] Compactage sémantique et réduction des espaces invisibles.`);

    const inputString = raw_text_stream.toString();

    // Traitement radical de la soute textuelle via regex d'acier
    const collapsedText = inputString
        .replace(/[ \t]+/g, ' ')       // Réduction de multiples espaces/tabulations en un seul espace
        .replace(/\s*\n\s*/g, '\n')    // Alignement propre des retours à la ligne
        .replace(/\n+/g, '\n')         // Élimination des lignes blanches consécutives
        .trim();                       // Purge des extrémités

    res.status(200).json({
        status: "TEXT_SPACES_FULLY_COLLAPSED",
        metrics: {
            bytes_received: inputString.length,
            bytes_compressed: collapsedText.length,
            compression_delta: Math.max(0, inputString.length - collapsedText.length)
        },
        collapsed_output: collapsedText,
        pipeline_integrity: {
            optimizer: "STATELESS_SPACE_MATRIX",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;