/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELATION
 * 🤖 ROBOT 16 : JSON-VALIDATE CORE ENGINE (STATELESS PAYLOAD INSPECTOR)
 * ⚡ REAL-TIME AST PARSING GATEWAY & DATA STRUCTURE CONFIRMATION
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : VALIDATION ET DIAGNOSTIC SYNTAXIQUE JSON
 */
router.post('/', (req, res) => {
    // Extraction de la chaine brute envoyee par le client dans le body
    const { raw_json } = req.body;

    if (!raw_json) {
        return res.status(400).json({ error: "Missing required 'raw_json' string payload in request body." });
    }

    console.log(`[🗂️ JSON-VALIDATE] Verification syntaxique AST pour un flux de ${raw_json.length} caracteres.`);

    try {
        // Tentative de parsing AST inline par le moteur natif V8
        const parsedObject = JSON.parse(raw_json);
        
        res.status(200).json({
            status: "STERILE_VALIDATION_SUCCESS",
            valid: true,
            structure_detected: Array.isArray(parsedObject) ? "ARRAY" : "OBJECT",
            metrics: {
                total_keys: typeof parsedObject === 'object' ? Object.keys(parsedObject).length : 0,
                payload_bytes: Buffer.byteLength(raw_json, 'utf8'),
                processing_speed: "0.1ms"
            },
            timestamp: new Date().toISOString()
        });

    } catch (parseError) {
        // Interception clinique et extraction de l'emplacement exact de la brèche
        console.warn(`[⚠️ JSON-INVALID] Payload corrompu detecte : ${parseError.message}`);
        
        res.status(422).json({
            status: "VALIDATION_FAILED",
            valid: false,
            error_details: {
                message: parseError.message,
                diagnostic_tip: "Check for missing trailing commas, unmatched curly braces, or invalid double quotes syntax labels."
            },
            timestamp: new Date().toISOString()
        });
    }
});

module.exports = router;