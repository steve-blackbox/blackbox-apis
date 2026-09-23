/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 44 : PII-MASKER CORE ENGINE (LOG SANITIZERS)
 * 🧼 STATELESS REGEX STREAM PROCESSOR TO OBFUSCATE SENSITIVE CARDS AND PII FOOTPRINTS
 */

const express = require('express');
const router = express.Router();

/** Luhn checksum — filters out plain 13-16 digit runs (order IDs, phone numbers,
 * tracking numbers...) that aren't actually valid card numbers, cutting false positives. */
function passesLuhnCheck(digits) {
    let sum = 0;
    let shouldDouble = false;
    for (let i = digits.length - 1; i >= 0; i--) {
        let d = parseInt(digits[i], 10);
        if (shouldDouble) {
            d *= 2;
            if (d > 9) d -= 9;
        }
        sum += d;
        shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
}

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
    let cardsMasked = 0;
    let emailsMasked = 0;

    // 💳 1. Regex de soute pour masquer les numéros de cartes bancaires (13 à 16 chiffres)
    // — verification Luhn reelle pour eviter de masquer des sequences de chiffres
    // innocentes (numeros de suivi, telephone, etc.).
    const creditCardPattern = /\b(?:\d[ -]*?){13,16}\b/g;
    maskedText = maskedText.replace(creditCardPattern, (match) => {
        const digitsOnly = match.replace(/[^\d]/g, '');
        if (!passesLuhnCheck(digitsOnly)) return match;
        cardsMasked++;
        const lastFour = digitsOnly.slice(-4);
        return `XXXX-XXXX-XXXX-${lastFour}`;
    });

    // 📧 2. Regex pour masquer partiellement les emails (ex: s***e@domain.com)
    const emailPattern = /\b([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b/g;
    maskedText = maskedText.replace(emailPattern, (match, p1, p2) => { emailsMasked++; return `${p1}***@${p2}`; });

    res.status(200).json({
        status: "PII_DATA_STREAM_SANITIZED",
        unmasked_length: raw_payload_text.length,
        masked_payload: maskedText,
        compliance_metrics: {
            cards_masked: cardsMasked,
            emails_masked: emailsMasked,
            // Factual statement about what this pass did, not a legal certification —
            // actual GDPR compliance depends on your full data pipeline, not a single
            // regex pass over one payload.
            obfuscation_type: "PARTIAL_REVERSION_BLOCK"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;