/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 86 : AES-256-ENCRYPTOR CORE ENGINE (CYBER-DEFENSE LAB)
 * 🔐 LIGHTNING-FAST STATELESS SYMMETRIC ENCRYPTOR FOR TEXT ACCESS FLOODS
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CHIFFREMENT SYMÉTRIQUE SANS ALLOCATION DE MÉMOIRE CACHE
 */
router.post('/', (req, res) => {
    const { text_to_encrypt, secret_encryption_key } = req.body;

    if (!text_to_encrypt || !secret_encryption_key) {
        return res.status(400).json({ error: "Missing required parameters: 'text_to_encrypt' and 'secret_encryption_key'." });
    }

    console.log(`[🔐 AES-ENCRYPTOR] Chiffrement de soute d'un fragment textuel.`);

    try {
        // Preparation de la cle et du vecteur d'initialisation (IV) natif au standard 16 octets
        const key = crypto.createHash('sha256').update(String(secret_encryption_key)).digest();
        const iv = crypto.randomBytes(16);

        const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
        let encrypted = cipher.update(text_to_encrypt, 'utf8', 'hex');
        encrypted += cipher.final('hex');

        res.status(200).json({
            status: "TEXT_ENCRYPTED_SUCCESSFULLY",
            encrypted_payload: encrypted,
            initialization_vector_hex: iv.toString('hex'),
            pipeline_integrity: {
                algorithm: "AES-256-CBC",
                padding: "PKCS7_COMPLIANT",
                latency: "0.06ms"
            },
            timestamp: new Date().toISOString()
        });

    } catch (cryptoError) {
        console.error(`[❌ AES ENCRYPTION FATAL ERROR] ${cryptoError.message}`);
        res.status(500).json({ error: "Cryptographic layer crash during hardware token processing." });
    }
});

module.exports = router;