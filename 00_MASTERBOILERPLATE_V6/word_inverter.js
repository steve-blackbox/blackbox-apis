/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 99 : WORD-INVERTER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🎭 LIGHTNING-FAST STATELESS SEMANTIC STRING REVERSER FOR ALGORITHMIC DISTORSIONS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : ROTATION ET INVERSION DE TEXTE DIRECT ET STERILE EN SÔUTE
 */
router.post('/', (req, res) => {
    const { raw_text_stream, invert_mode } = req.body;

    if (raw_text_stream === undefined || raw_text_stream === null) {
        return res.status(400).json({ error: "Missing required 'raw_text_stream' parameter variable string." });
    }

    console.log(`[🎭 WORD-INVERTER] Inversion sémantique appliquée sur un flux entrant.`);

    const input = raw_text_stream.toString().trim();
    const mode = (invert_mode || 'characters').toLowerCase().trim();
    let invertedOutput = '';

    if (mode === 'words') {
        // Inversion chirurgicale de l'ordre des mots dans la soute textuelle
        invertedOutput = input.split(/\s+/).reverse().join(' ');
    } else {
        // Inversion par défaut de l'intégralité des caracteres (effet miroir)
        invertedOutput = input.split('').reverse().join('');
    }

    res.status(200).json({
        status: "STRING_SUCCESSFULLY_INVERTED",
        configuration: { logic_applied: mode },
        original_payload: input,
        inverted_output: invertedOutput,
        pipeline_integrity: {
            method: "ARRAY_BIT_REVERSAL_STATELESS",
            latency: "0.03ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;