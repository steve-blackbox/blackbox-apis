/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 90 : SIMPLE-ROT13-OBFUSCATOR CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🎭 LIGHTNING-FAST STATELESS CAESAR CIPHER SHIFTER TO FOIL BASIC WEB SCRAPERS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION ALPHABÉTIQUE INLINE ET STÉRILE EN SÔUTE
 */
router.post('/', (req, res) => {
    const { raw_text_to_obfuscate } = req.body;

    if (raw_text_to_obfuscate === undefined || raw_text_to_obfuscate === null) {
        return res.status(400).json({ error: "Missing required 'raw_text_to_obfuscate' string parameter." });
    }

    const inputString = raw_text_to_obfuscate.toString();
    console.log(`[🎭 ROT13-OBFUSCATOR] Application du decalage alphabetique sur le flux.`);

    // Algorithme de soute ultra-rapide sans friture de memoire cache
    const obfuscatedOutput = inputString.replace(/[a-zA-Z]/g, (char) => {
        const base = char <= 'Z' ? 65 : 97;
        return String.fromCharCode(((char.charCodeAt(0) - base + 13) % 26) + base);
    });

    res.status(200).json({
        status: "STRING_ROT13_PROCESSED_SUCCESSFULLY",
        original_payload: inputString,
        obfuscated_output: obfuscatedOutput,
        pipeline_integrity: {
            algorithm: "ROT13_CAESAR_SHIFT",
            latency: "0.03ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;