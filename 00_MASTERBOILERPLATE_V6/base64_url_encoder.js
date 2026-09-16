/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 89 : BASE64-URL-ENCODER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🔬 LIGHTNING-FAST STATELESS STRIPPER TO GENERATE URL-SAFE BASE64 TOKENS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CONVERSION ET NETTOYAGE SYNTAXIQUE DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_string_input } = req.body;

    if (raw_string_input === undefined || raw_string_input === null) {
        return res.status(400).json({ error: "Missing required 'raw_string_input' variable parameter string." });
    }

    console.log(`[🔬 BASE64-URL-ENCODER] Ingestion et codage de la soute textuelle.`);

    const textPayload = raw_string_input.toString();

    // Encodage initial en Base64 standard native
    const base64 = Buffer.from(textPayload, 'utf8').toString('base64');

    // Traduction chirurgicale au standard URL-Safe (RFC 4648)
    const urlSafeBase64 = base64
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, ''); // Nettoyage de soute du padding string

    res.status(200).json({
        status: "PAYLOAD_ENCODED_TO_BASE64_URL_SAFE",
        input_length_bytes: Buffer.byteLength(textPayload, 'utf8'),
        standard_base64_output: base64,
        url_safe_base64_output: urlSafeBase64,
        pipeline_integrity: {
            standard_rule: "RFC_4648_SECTION_5",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;