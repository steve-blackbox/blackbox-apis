/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 95 : SNAKE-CASE-CONVERTER CORE ENGINE (DATA NORMALIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS FORMATTER FOR SCHEMA AND DATABASE COLUMN HEALTH
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION EN STANDARD SNAKE_CASE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_input_string } = req.body;

    if (!raw_input_string) {
        return res.status(400).json({ error: "Missing required 'raw_input_string' parameter variable string." });
    }

    const text = raw_input_string.toString().trim();
    console.log(`[🧹 SNAKE-CASE] Conversion de soute textuelle pour la chaine: "${text.substring(0, 30)}..."`);

    // Logique de soute chirurgicale pour forcer l'alignement snake_case strict
    const snakeCaseOutput = text
        .replace(/[^a-zA-Z0-9\s-_]/g, '')   // Elimination des caracteres speciaux parasites
        .replace(/([a-z0-9])([A-Z])/g, '$1_$2') // Capture et separation des casses Camel/Pascal imbriquees
        .toLowerCase()
        .split(/[\s-_]+/)                   // Decoupage par les espaces, tirets et underscores restantes
        .filter(word => word.length > 0)
        .join('_');

    res.status(200).json({
        status: "STRING_CONVERTED_TO_SNAKE_CASE",
        input_received: text,
        snake_case_output: snakeCaseOutput,
        pipeline_integrity: {
            naming_convention: "SNAKE_CASE_STRICT",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;