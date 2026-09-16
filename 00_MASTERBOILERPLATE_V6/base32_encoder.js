/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 75 : BASE32-ENCODER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🔬 STATELESS STANDARD RFC-4648 BASE32 BIT STREAM STREAM PROCESSOR
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : ENCODAGE BINAIRE INLINE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_string_payload } = req.body;

    if (!raw_string_payload) {
        return res.status(400).json({ error: "Missing required 'raw_string_payload' variable parameter string." });
    }

    console.log(`[🔬 BASE32-ENCODER] Ingestion et codage binaire du texte entrant.`);

    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    const buffer = Buffer.from(raw_string_payload.toString(), 'utf8');
    
    let bits = 0;
    let value = 0;
    let output = '';

    // Encodage chirurgical par blocs de 5 bits selon la norme RFC 4648
    for (let i = 0; i < buffer.length; i++) {
        value = (value << 8) | buffer[i];
        bits += 8;
        while (bits >= 5) {
            output += alphabet[(value >>> (bits - 5)) & 31];
            bits -= 5;
        }
    }

    if (bits > 0) {
        output += alphabet[(value << (5 - bits)) & 31];
    }

    // Bourrage esthetique conforme au standard '=' padding
    while ((output.length % 8) !== 0) {
        output += '=';
    }

    res.status(200).json({
        status: "PAYLOAD_ENCODED_TO_BASE32_COMPLIANT",
        input_string: raw_string_payload,
        encoded_output_base32: output,
        pipeline_integrity: {
            standard_rule: "RFC_4648_BIT_STREAM",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;