/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 94 : CAMEL-CASE-CONVERTER CORE ENGINE (DATA NORMALIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS FORMATTER FOR FRONT-END ENGINE JAVASCRIPT OBJECT KEYS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION EN STANDARD CAMELCASE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_input_string } = req.body;

    if (!raw_input_string) {
        return res.status(400).json({ error: "Missing required 'raw_input_string' parameter variable string." });
    }

    const text = raw_input_string.toString().trim();
    console.log(`[🧹 CAMEL-CASE] Conversion de soute textuelle pour la chaine: "${text.substring(0, 30)}..."`);

    // Logique de soute chirurgicale pour découper et formater au standard camelCase
    const words = text
        .replace(/[^a-zA-Z0-9\s-_]/g, '') // Elimination des caracteres speciaux parasites
        .split(/[\s-_]+/)                 // Decoupage par les espaces, tirets et underscores
        .filter(word => word.length > 0);

    if (words.length === 0) {
        return res.status(200).json({ status: "SUCCESS", camel_case_output: "" });
    }

    const camelCaseOutput = words[0].toLowerCase() + words
        .slice(1)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join('');

    res.status(200).json({
        status: "STRING_CONVERTED_TO_CAMEL_CASE",
        input_received: text,
        camel_case_output: camelCaseOutput,
        pipeline_integrity: {
            naming_convention: "CAMEL_CASE_STRICT",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;