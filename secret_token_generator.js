/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 74 : SECRET-TOKEN-GENERATOR CORE ENGINE (NUMERIC HASH LAB)
 * 🔑 STATELESS CRYPTOGRAPHICALLY SECURE HARDENED TOKEN GENERATOR FOR SYSTEM ACCESS
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

/**
 * 📥 ROUTE CORE : PRODUC_TION DYNAMIQUE ET SÈCHE DE JETONS DE HAUTE ENTROPIE
 */
router.post('/', (req, res) => {
    const { byte_length, output_format } = req.body;

    // Fixation sécurisée de la longueur de soute entre 16 et 128 octets max
    const length = Math.min(Math.max(parseInt(byte_length) || 32, 16), 128);
    const format = (output_format || 'hex').toLowerCase().trim();

    const allowedFormats = ['hex', 'base64', 'url'];
    if (!allowedFormats.includes(format)) {
        return res.status(400).json({ error: "Unsupported 'output_format'. Use 'hex', 'base64' or 'url'." });
    }

    console.log(`[🔑 SECRET-TOKEN] Generation d'une cle securisee de ${length} octets au format: ${format}`);

    try {
        const buffer = crypto.randomBytes(length);
        let token = '';

        if (format === 'hex') {
            token = buffer.toString('hex');
        } else if (format === 'base64') {
            token = buffer.toString('base64');
        } else if (format === 'url') {
            token = buffer.toString('base64')
                .replace(/\+/g, '-')
                .replace(/\//g, '_')
                .replace(/=+$/, ''); // Format URL-Safe sterile
        }

        res.status(200).json({
            status: "CRYPTOGRAPHIC_TOKEN_GENERATED",
            configured_bytes: length,
            format_selected: format,
            generated_secret_token: token,
            pipeline_integrity: {
                entropy_source: "NODE_CRYPTO_RANDOM_BYTES",
                security_layer: "UNPREDICTABLE_HIGH_ENTROPY"
            },
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        res.status(500).json({ error: "Fatal anomaly inside hardware entropy generator engine." });
    }
});

module.exports = router;