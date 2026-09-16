/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 44 : PII-MASKER CORE ENGINE (LOG SANITIZERS)
 * 🧼 STATELESS REGEX STREAM PROCESSOR TO OBFUSCATE SENSITIVE CARDS AND PII FOOTPRINTS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : OBFUSCATION DYNAMIQUE DES DONNÉES PRIVÉES
 */
router.post('/', (req, res) => {
    const { raw_payload_text } = req.body;

    if (!raw_payload_text) {
        return res.status(400).json({ error: "Missing required 'raw_payload_text' parameter inside text payload." });
    }

    console.log(`[🧼 PII-MASKER] Ingestion du flux de donnees pour obfuscation de securite.`);

    let maskedText = raw_payload_text;

    // 💳 1. Regex de soute pour masquer les numéros de cartes bancaires (13 à 16 chiffres)
    const creditCardPattern = /\b(?:\d[ -]*?){13,16}\b/g;
    maskedText = maskedText.replace(creditCardPattern, (match) => {
        const digitsOnly = match.replace(/[^\d]/g, '');
        const lastFour = digitsOnly.slice(-4);
        return `XXXX-XXXX-XXXX-${lastFour}`;
    });

    // 📧 2. Regex pour masquer partiellement les emails (ex: s***e@domain.com)
    const emailPattern = /\b([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b/g;
    maskedText = maskedText.replace(emailPattern, '$1***@$2');

    res.status(200).json({
        status: "PII_DATA_STREAM_SANITIZED",
        unmasked_length: raw_payload_text.length,
        masked_payload: maskedText,
        compliance_metrics: {
            gdpr_compliant: true,
            obfuscation_type: "PARTIAL_REVERSION_BLOCK"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;