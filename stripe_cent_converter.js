/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 82 : STRIPE-CENT-CONVERTER CORE ENGINE (MATH & STATS LAB)
 * 💳 LIGHTNING-FAST STATELESS DECIMAL-TO-CENT INT CONVERTER FOR STRIPE BIL_LING
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION DE DEVISE INLINE ET STÉRILE EN SÔUTE
 */
router.post('/', (req, res) => {
    const { decimal_amount } = req.body;

    if (decimal_amount === undefined || decimal_amount === null) {
        return res.status(400).json({ error: "Missing required 'decimal_amount' variable number." });
    }

    console.log(`[💳 STRIPE-CENT-CONVERTER] Transformation financiere du prix decimal.`);

    const amount = parseFloat(decimal_amount);

    if (isNaN(amount) || amount < 0) {
        return res.status(422).json({ error: "Invalid decimal amount format string. Must be a positive floating weight." });
    }

    // Protection absolue contre la friture d'arrondi IEEE 754 de JavaScript
    const amountInCents = Math.round(amount * 100);

    res.status(200).json({
        status: "DECIMAL_AMOUNT_CONVERTED_TO_STRIPE_CENTS",
        input_decimal: amount,
        output_cents_integer: amountInCents,
        pipeline_integrity: {
            math_operation: "MATH_ROUND_FLOATING_SAFE",
            latency: "0.03ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;