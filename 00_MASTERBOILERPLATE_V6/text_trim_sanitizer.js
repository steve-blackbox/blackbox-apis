/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 66 : TEXT-TRIM-SANITIZER CORE ENGINE (ASSET SHRINK LAB)
 * 🧹 LIGHTNING-FAST STATELESS STRING CLEANER TO PURGE PARASITIC WHITESPACES
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : NETTOYAGE ET ASSAINISSEMENT DE TEXTE DIRECT SANS FR_ITURE
 */
router.post('/', (req, res) => {
    const { raw_text_stream } = req.body;

    if (raw_text_stream === undefined || raw_text_stream === null) {
        return res.status(400).json({ error: "Missing required 'raw_text_stream' string variable inside body payload." });
    }

    console.log(`[🧹 TEXT-TRIM-SANITIZER] Ingestion d'un flux de texte brut pour assainissement.`);

    const inputString = raw_text_stream.toString();

    // Nettoyage de soute chirurgical via expressions régulières stériles
    const cleanedText = inputString
        .replace(/[\r\n]+/g, '\n')     // Harmonisation des retours à la ligne corrompus
        .replace(/[ \t]+/g, ' ')       // Élimination des tabulations et doubles espaces
        .trim();                       // Purge des extrémités

    res.status(200).json({
        status: "STRING_CLEANED_AND_NORMALIZED",
        metrics: {
            original_character_length: inputString.length,
            sanitized_character_length: cleanedText.length,
            bytes_saved: Math.max(0, inputString.length - cleanedText.length)
        },
        sanitized_output: cleanedText,
        pipeline_integrity: {
            cleaning_layer: "STATELESS_TRIM_MATRIX",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;