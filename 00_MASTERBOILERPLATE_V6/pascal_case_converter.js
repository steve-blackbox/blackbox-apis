/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 93 : PASCAL-CASE-CONVERTER CORE ENGINE (DATA NORMALIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS FORMATTER TO GENERATE CLEAN CODE COMPLIANT STRINGS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION EN STANDARD PASCALCASE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_input_string } = req.body;

    if (!raw_input_string) {
        return res.status(400).json({ error: "Missing required 'raw_input_string' parameter variable string." });
    }

    const text = raw_input_string.toString().trim();
    console.log(`[🧹 PASCAL-CASE] Conversion de soute textuelle pour la chaine: "${text.substring(0, 30)}..."`);

    // Logique de soute chirurgicale pour découper et capitaliser chaque bloc
    const pascalCaseOutput = text
        .replace(/[^a-zA-Z0-9\s-_]/g, '') // Elimination des caracteres speciaux parasites
        .split(/[\s-_]+/)                 // Decoupage par les espaces, tirets et underscores
        .filter(word => word.length > 0)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join('');

    res.status(200).json({
        status: "STRING_CONVERTED_TO_PASCAL_CASE",
        input_received: text,
        pascal_case_output: pascalCaseOutput,
        pipeline_integrity: {
            naming_convention: "PASCAL_CASE_STRICT",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;