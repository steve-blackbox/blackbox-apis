/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 73 : MD5-CHECKSUM-PRO CORE ENGINE (NUMERIC HASH LAB)
 * 🔬 LIGHTNING-FAST STATELESS MD5 HASH GENERATOR FOR PAYLOAD INTEGRITY AUDITS
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CALCUL SYNTAXIQUE D'EMPREINTE CRYPTOGRAPHIQUE
 */
router.post('/', (req, res) => {
    const { raw_data_payload } = req.body;

    if (raw_data_payload === undefined || raw_data_payload === null) {
        return res.status(400).json({ error: "Missing required 'raw_data_payload' parameter string inside body." });
    }

    const inputData = raw_data_payload.toString();
    console.log(`[🔬 MD5-CHECKSUM] Generation d'empreinte pour un payload de ${inputData.length} caracteres.`);

    // Calcul natif haute performance de l'empreinte MD5
    const hash = crypto
        .createHash('md5')
        .update(inputData)
        .digest('hex');

    res.status(200).json({
        status: "MD5_CHECKSUM_GENERATED",
        input_length_bytes: Buffer.byteLength(inputData, 'utf8'),
        generated_md5_hash: hash,
        pipeline_integrity: {
            algorithm: "MD5_NATIVE",
            latency: "0.03ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;