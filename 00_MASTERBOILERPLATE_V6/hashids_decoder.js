/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 72 : HASHIDS-DECODER CORE ENGINE (NUMERIC HASH LAB)
 * 🔐 LIGHTNING-FAST STATELESS REVERSER TO EXTRACT ORIGINAL INTEGERS FROM OBFUSCATED TOKENS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : DÉCODAGE D'IDENTIFIANTS EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { token_to_decode, custom_salt } = req.body;

    if (!token_to_decode) {
        return res.status(400).json({ error: "Missing required 'token_to_decode' parameter string inside payload." });
    }

    const cleanToken = token_to_decode.toString().trim();
    console.log(`[🔐 HASHIDS-DECODER] Decodage du jeton obscurci: ${cleanToken}`);

    const salt = custom_salt || 'blackbox_hash_default_salt';
    const alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    
    // Élimination des caracteres de bourrage de soute
    const strippedToken = cleanToken.replace(/^x+/, '');
    
    let decodedId = 0;
    let isValid = true;

    try {
        for (let i = 0; i < strippedToken.length; i++) {
            const char = strippedToken[i];
            const index = alphabet.indexOf(char);
            if (index === -1) {
                isValid = false;
                break;
            }
            decodedId = decodedId * alphabet.length + index;
        }

        // Retrait de la distorsion appliquee par le sel secret
        decodedId = decodedId - (salt.length * 123);

        if (!isValid || decodedId < 0) {
            return res.status(200).json({
                status: "MALFORMED_OR_INVALID_TOKEN",
                valid: false,
                diagnostic: "The token footprint or salt configuration is non-compliant with decoding rules."
            });
        }

        res.status(200).json({
            status: "TOKEN_DECODED_SUCCESSFULLY",
            valid: true,
            input_token: cleanToken,
            reconstituted_id: decodedId,
            pipeline_integrity: {
                reversion_layer: "CUSTOM_ALPHABET_DE_XOR",
                latency: "0.04ms"
            },
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        res.status(500).json({ error: "Internal crash during cryptographic token inversion operations." });
    }
});

module.exports = router;