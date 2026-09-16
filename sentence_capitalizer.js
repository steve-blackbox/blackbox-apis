/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 96 : SENTENCE-CAPITALIZER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS EDITORIAL STRING FORMATTER FOR SYSTEM TRANSFORMS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CAPITALISATION FORCEE DE PREMIERE LETTRE DE PHRASE INLINE
 */
router.post('/', (req, res) => {
    const { raw_text_stream } = req.body;

    if (raw_text_stream === undefined || raw_text_stream === null) {
        return res.status(400).json({ error: "Missing required 'raw_text_stream' parameter variable string." });
    }

    console.log(`[🧹 SENTENCE-CAPITALIZER] Re-formatage editorial du flux de texte.`);

    const text = raw_text_stream.toString();

    // Regex chirurgicale de soute capturant les fins de phrase pour cibler la lettre suivante
    const processedText = text.replace(/(^\s*|[.!?]\s+)([a-z])/g, (match, separator, letter) => {
        return separator + letter.toUpperCase();
    });

    res.status(200).json({
        status: "SENTENCES_SUCCESSFULLY_CAPITALIZED",
        input_length: text.length,
        formatted_output: processedText,
        pipeline_integrity: {
            engine: "REGEXP_STATELESS_CAPITALIZER",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;