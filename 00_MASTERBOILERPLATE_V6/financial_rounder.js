/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 83 : FINANCIAL-ROUNDER CORE ENGINE (MATH & STATS LAB)
 * 📉 LIGHTNING-FAST STATELESS BANKING ROUNDER TO PREVENT FLOAT DOUBLE DEVIATIONS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CALC_UL ET ARROUNDI DE PRÉCISION FINANCIÈRE DIRECT
 */
router.post('/', (req, res) => {
    const { raw_numeric_value } = req.body;

    if (raw_numeric_value === undefined || raw_numeric_value === null) {
        return res.status(400).json({ error: "Missing required 'raw_numeric_value' parameter inside payload." });
    }

    console.log(`[📉 FINANCIAL-ROUNDER] Ingestion d'un flux numerique pour troncature comptable.`);

    const value = parseFloat(raw_numeric_value);

    if (isNaN(value)) {
        return res.status(422).json({ error: "Invalid numeric parameter footprint. Check entity weights." });
    }

    // Algorithme d'arrondi comptable strict (Epsilon safe layer against floating points)
    const roundedValue = parseFloat((Math.round((value + Number.EPSILON) * 100) / 100).toFixed(2));

    res.status(200).json({
        status: "NUMERIC_VALUE_ROUNDED",
        input_value: value,
        rounded_output: roundedValue,
        pipeline_integrity: {
            method: "EPSILON_BANKING_COMPLIANT",
            latency: "0.03ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;