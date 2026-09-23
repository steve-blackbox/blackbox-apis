/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 43 : PHONE-SANITIZER CORE ENGINE (HEAVY REGEX LAB)
 * 📞 STATELESS E.164 INTERNATIONAL PHONE STANDARDIZER FOR CRM INTEGRITY
 */

const express = require('express');
const router = express.Router();

// Longueur attendue du National Significant Number (hors indicatif pays) pour
// quelques indicatifs courants — permet une validation plus fine que le simple
// gabarit E.164 générique, sans prétendre couvrir tous les plans de numérotation.
const NSN_LENGTH_BY_PREFIX = {
    '33': 9,   // France
    '1': 10,   // USA / Canada
    '44': 10,  // UK
    '49': [10, 11], // Germany
    '34': 9,   // Spain
    '39': [9, 10], // Italy
    '32': [8, 9], // Belgium
    '41': 9,   // Switzerland
    '351': 9,  // Portugal
    '31': 9    // Netherlands
};

/**
 * 📥 ROUTE CORE : NETTOYAGE ET STRUCTURATION D'UN NUMÉRO DE TÉLÉPHONE
 */
router.post('/', (req, res) => {
    const { raw_phone_string, default_country_code } = req.body;

    if (!raw_phone_string) {
        return res.status(400).json({ error: "Missing required 'raw_phone_string' string parameter." });
    }

    console.log(`[📞 PHONE-SANITIZER] Ingestion et filtrage de soute pour la chaine: ${raw_phone_string}`);

    const startTime = process.hrtime.bigint();

    // Élimination agressive de tout ce qui n'est pas un chiffre ou le signe +
    let cleaned = raw_phone_string.replace(/[^\d+]/g, '');

    // Le fallback France reste disponible mais est désormais explicitement signalé
    // dans la réponse ("assumed_country_prefix") plutôt que silencieux, pour éviter
    // toute confusion côté appelant quand aucun indicatif n'a été fourni.
    const countryWasAssumed = !default_country_code && !cleaned.startsWith('+') && !cleaned.startsWith('00');
    const prefix = default_country_code ? default_country_code.toString().replace(/[^\d]/g, '') : '33';

    // Gestion du cas où l'utilisateur commence par un zéro local (ex: 06...)
    if (cleaned.startsWith('0') && !cleaned.startsWith('00')) {
        cleaned = `+${prefix}${cleaned.substring(1)}`;
    } else if (cleaned.startsWith('00')) {
        cleaned = `+${cleaned.substring(2)}`;
    } else if (!cleaned.startsWith('+')) {
        cleaned = `+${prefix}${cleaned}`;
    }

    // Validation finale de soute de la norme E.164 (signe + suivi de 10 à 15 chiffres max)
    const e164Pattern = /^\+[1-9]\d{1,14}$/;
    const isValidE164 = e164Pattern.test(cleaned);

    // Validation additionnelle de la longueur du NSN quand l'indicatif est reconnu.
    let nsnLengthValid = true;
    let matchedPrefix = null;
    if (isValidE164) {
        const digitsAfterPlus = cleaned.slice(1);
        matchedPrefix = Object.keys(NSN_LENGTH_BY_PREFIX)
            .sort((a, b) => b.length - a.length)
            .find(p => digitsAfterPlus.startsWith(p));
        if (matchedPrefix) {
            const nsn = digitsAfterPlus.slice(matchedPrefix.length);
            const expected = NSN_LENGTH_BY_PREFIX[matchedPrefix];
            nsnLengthValid = Array.isArray(expected) ? expected.includes(nsn.length) : nsn.length === expected;
        }
    }

    const elapsedMs = Number(process.hrtime.bigint() - startTime) / 1e6;

    if (!isValidE164 || !nsnLengthValid) {
        return res.status(200).json({
            status: "NON_COMPLIANT_PHONE_FORMAT",
            valid: false,
            input_received: raw_phone_string,
            sanatized_attempt: cleaned,
            diagnostic: !isValidE164
                ? "The string length or prefix violates international E.164 baseline requirements."
                : `National number length does not match the expected pattern for country prefix +${matchedPrefix}.`
        });
    }

    res.status(200).json({
        status: "PHONE_STANDARDIZED_SUCCESSFULLY",
        valid: true,
        input_received: raw_phone_string,
        e164_format: cleaned,
        assumed_country_prefix: countryWasAssumed ? `+${prefix}` : null,
        routing_metrics: {
            telecom_standard: "E.164_COMPLIANT",
            nsn_length_checked: !!matchedPrefix,
            latency_ms: Number(elapsedMs.toFixed(3))
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;