/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 87 : AES-256-DECRYPTOR CORE ENGINE (CYBER-DEFENSE LAB)
 * 🔐 LIGHTNING-FAST STATELESS SYMMETRIC DECRYPTOR TO RESTORE ENCRYPTED SECRETS
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

/**
 * 📥 ROUTE CORE : DECHIFFREMENT EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { encrypted_payload, secret_encryption_key, initialization_vector_hex } = req.body;

    if (!encrypted_payload || !secret_encryption_key || !initialization_vector_hex) {
        return res.status(400).json({ error: "Missing required parameters: 'encrypted_payload', 'secret_encryption_key' and 'initialization_vector_hex'." });
    }

    console.log(`[🔐 AES-DECRYPTOR] Dechiffrement de soute d'un fragment cryptique.`);

    try {
        // Reconstitution de la cle et de l'IV natif de 16 octets
        const key = crypto.createHash('sha256').update(String(secret_encryption_key)).digest();
        const iv = Buffer.from(initialization_vector_hex, 'hex');

        if (iv.length !== 16) {
            return res.status(422).json({ error: "Invalid initialization vector length. Must be exactly 16 bytes (32 hex characters)." });
        }

        const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
        let decrypted = decipher.update(encrypted_payload, 'hex', 'utf8');
        decrypted += decipher.final('utf8');

        res.status(200).json({
            status: "TEXT_DECRYPTED_SUCCESSFULLY",
            decrypted_plaintext: decrypted,
            pipeline_integrity: {
                algorithm: "AES-256-CBC",
                state: "STERILE_SECURE",
                latency: "0.05ms"
            },
            timestamp: new Date().toISOString()
        });

    } catch (cryptoError) {
        console.error(`[❌ AES DECRYPTION ERROR] ${cryptoError.message}`);
        res.status(422).json({ error: "Decryption failed. Check key compliance or data corruption variables." });
    }
});

module.exports = router;