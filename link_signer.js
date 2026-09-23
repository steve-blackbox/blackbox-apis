/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 54 : LINK-SIGNER CORE ENGINE (LINK PROTECTION LAB)
 * 🔐 LIGHTNING-FAST STATELESS HMAC TOKEN GENERATOR FOR SECURE EXPIRING LINKS
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CALCUL ET SIGNATURE CRYPTOGRAPHIQUE DE LIENS ÉPHÉMÈRES
 */
router.post('/', (req, res) => {
    const { base_url, expiration_minutes, secret_salt } = req.body;

    if (!base_url || !expiration_minutes) {
        return res.status(400).json({ error: "Missing required params: 'base_url' string and 'expiration_minutes' integer." });
    }
    if (!secret_salt || typeof secret_salt !== 'string' || secret_salt.length < 8) {
        return res.status(400).json({ error: "Missing or too short 'secret_salt' string (minimum 8 characters). A predictable or default salt would make signatures forgeable — always supply your own." });
    }

    let parsedBaseUrl;
    try {
        parsedBaseUrl = new URL(base_url);
    } catch (e) {
        return res.status(400).json({ error: "Invalid 'base_url': must be a well-formed absolute URL." });
    }

    console.log(`[🔐 LINK-SIGNER] Generation d'une signature cryptographique pour le lien : ${base_url}`);

    const startTime = process.hrtime.bigint();

    // Calcul de l'expiration temporelle Unix timestamp en soute
    const expires = Math.floor(Date.now() / 1000) + (parseInt(expiration_minutes) * 60);

    // Generation native SHA256 sterile du jeton d'acces
    const signature = crypto
        .createHmac('sha256', secret_salt)
        .update(`${base_url}?expires=${expires}`)
        .digest('hex');

    // Assemblage final de l'URL securisee
    const signedUrl = `${base_url}?expires=${expires}&signature=${signature}`;

    const elapsedMs = Number(process.hrtime.bigint() - startTime) / 1e6;

    res.status(200).json({
        status: "URL_CRYPTOGRAPHICALLY_SIGNED",
        original_target: base_url,
        expires_timestamp: expires,
        generated_signature: signature,
        secured_endpoint_url: signedUrl,
        pipeline_integrity: {
            crypto_algorithm: "HMAC-SHA256",
            latency_ms: Number(elapsedMs.toFixed(3))
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;