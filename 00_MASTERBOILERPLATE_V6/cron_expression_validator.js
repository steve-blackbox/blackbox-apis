/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 62 : CRON-EXPRESSION-VALIDATOR CORE ENGINE (CRON & SCHEDULER LAB)
 * ⏱️ STATELESS AUTOMATED INSPECTOR TO VALIDATE CRON STRUCTURES UPSTREAM
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION SYNTAXIQUE DES REGEX DE PLANIFICATION CRON
 */
router.post('/', (req, res) => {
    const { cron_expression } = req.body;

    if (!cron_expression) {
        return res.status(400).json({ error: "Missing required 'cron_expression' variable parameter string." });
    }

    const targetCron = cron_expression.trim();
    console.log(`[⏱️ CRON-VALIDATOR] Scan de soute syntaxique pour la chaine : ${targetCron}`);

    // Regex chirurgicale de validation pour le standard standardise Cron (5 sections)
    const cronRegex = /^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]))\s+(\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3]))\s+(\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1]))\s+(\*|([1-9]|1[0-1])|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\*\/([1-9]|1[0-1]))\s+(\*|([0-6])|sun|mon|tue|wed|thu|fri|sat)\s*$/i;

    const isValid = cronRegex.test(targetCron);

    if (!isValid) {
        return res.status(200).json({
            status: "MALFORMED_CRON_SYNTAX",
            valid: false,
            input_received: targetCron,
            diagnostic: "The cron segment parameters format violates structural scheduling boundaries."
        });
    }

    res.status(200).json({
        status: "CRON_EXPRESSION_VALIDATED",
        valid: true,
        input_received: targetCron,
        architecture: {
            parsing_standard: "V5_SEGMENTS_COMPLIANT",
            state: "STERILE_SECURE"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;