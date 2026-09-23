/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 55 : LINK-VALIDATOR CORE ENGINE (LINK PROTECTION LAB)
 * 🔬 STATELESS SHA-256 CRYPTOGRAPHIC INTEGRITY CHECKER FOR EXPIRING ENDPOINTS
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

/**
 * 📥 ROUTE CORE : VERIFICATION DES PARAMETRES ET DU TIMESTAMP D'EXPIRATION
 */
router.post('/', (req, res) => {
    const { signed_url, secret_salt } = req.body;

    if (!signed_url) {
        return res.status(400).json({ error: "Missing required 'signed_url' parameter string." });
    }
    if (!secret_salt || typeof secret_salt !== 'string' || secret_salt.length < 8) {
        return res.status(400).json({ error: "Missing or too short 'secret_salt' string (minimum 8 characters). Must match the salt used by link_signer for this URL." });
    }

    console.log(`[🔬 LINK-VALIDATOR] Audit de signature cryptographique pour l'URL cliente.`);

    try {
        const urlObj = new URL(signed_url);
        const baseUrl = urlObj.origin + urlObj.pathname;
        const expires = urlObj.searchParams.get('expires');
        const signature = urlObj.searchParams.get('signature');

        if (!expires || !signature) {
            return res.status(200).json({
                status: "MALFORMED_SECURE_LINK",
                valid: false,
                diagnostic: "Mandatory security query tokens ('expires' or 'signature') are completely missing."
            });
        }

        // ⏱️ 1. Contrôle du dépassement de la soute temporelle Unix
        const currentTimestamp = Math.floor(Date.now() / 1000);
        if (currentTimestamp > parseInt(expires)) {
            return res.status(200).json({
                status: "LINK_EXPIRED",
                valid: false,
                diagnostic: `The token lifetime window closed. Delta override: ${currentTimestamp - parseInt(expires)} seconds.`
            });
        }

        // 🔐 2. Recalcul algorithmique pour traquer la falsification
        const expectedSignature = crypto
            .createHmac('sha256', secret_salt)
            .update(`${baseUrl}?expires=${expires}`)
            .digest('hex');

        // Constant-time comparison to avoid leaking signature bytes via response timing.
        const signatureBuffer = Buffer.from(signature, 'utf8');
        const expectedBuffer = Buffer.from(expectedSignature, 'utf8');
        const signaturesMatch = signatureBuffer.length === expectedBuffer.length &&
            crypto.timingSafeEqual(signatureBuffer, expectedBuffer);

        if (!signaturesMatch) {
            return res.status(200).json({
                status: "SIGNATURE_MISMATCH_ATTACK_DETECTED",
                valid: false,
                diagnostic: "The payload hash string has been altered. Access violently restricted."
            });
        }

        res.status(200).json({
            status: "CRYPTOGRAPHIC_LINK_VALIDATED",
            valid: true,
            target_cleared: baseUrl,
            time_remaining_seconds: parseInt(expires) - currentTimestamp,
            security_check: {
                tampering_attempt: "NONE_DETECTED",
                gateway_clearance: "APPROVED"
            },
            timestamp: new Date().toISOString()
        });

    } catch (urlError) {
        console.error(`[❌ CRYPTO AUDIT ERROR] Format d'URL invalide : ${urlError.message}`);
        res.status(400).json({ error: "Invalid signed URL footprint parsed string format." });
    }
});

module.exports = router;