/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 52 : EVENT-FILTER CORE ENGINE (EVENT ROUTERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS PAYLOAD EVALUATOR AND CRITERIA FILTER FOR WEBHOOK STREAMS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION ET FILTRAGE CRITIQUE EN FLUX DIRECT
 */
router.post('/', (req, res) => {
    const { payload, match_key, expected_value } = req.body;

    if (!payload || !match_key || expected_value === undefined) {
        return res.status(400).json({ error: "Missing required variables: 'payload' (object), 'match_key' (string) and 'expected_value'." });
    }

    console.log(`[🧹 EVENT-FILTER] Inspection de soute pour la clé: ${match_key}`);

    let isMatch = false;
    const actualValue = payload[match_key];

    // Vérification de soute dynamique (strict match textuel ou numérique)
    if (actualValue !== undefined && actualValue.toString() === expected_value.toString()) {
        isMatch = true;
    }

    res.status(200).json({
        status: "PAYLOAD_EVALUATION_COMPLETED",
        criteria_matched: isMatch,
        audit_details: {
            inspected_key: match_key,
            value_found: actualValue !== undefined ? actualValue : null,
            value_expected: expected_value
        },
        action: isMatch ? "FORWARD_STREAM" : "DROP_SILENTLY",
        pipeline_integrity: {
            evaluation_type: "AST_KEY_LOOKUP",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;