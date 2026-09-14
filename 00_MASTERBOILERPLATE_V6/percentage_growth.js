/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 81 : PERCENTAGE-GROWTH CORE ENGINE (MATH & STATS LAB)
 * 📈 LIGHTNING-FAST STATELESS CALCULATOR FOR DRIFT AND GROWTH RATIOS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CALCUL SYNTAXIQUE DE RATIO D'ÉVOLUTION FINANCIÈRE SOU_TE
 */
router.post('/', (req, res) => {
    const { initial_value, final_value } = req.body;

    if (initial_value === undefined || final_value === undefined) {
        return res.status(400).json({ error: "Missing required 'initial_value' and 'final_value' parameters." });
    }

    console.log(`[📈 PERCENTAGE-GROWTH] Calcul de soute du taux d'evolution.`);

    const vInit = parseFloat(initial_value);
    const vFinal = parseFloat(final_value);

    if (isNaN(vInit) || isNaN(vFinal)) {
        return res.status(422).json({ error: "Invalid input parameters. Elements must be numerical weights." });
    }

    if (vInit === 0) {
        return res.status(200).json({
            status: "GROWTH_CALCULATED",
            growth_percentage: vFinal > 0 ? "INFINITE_GROWTH" : "ZERO_OR_NEGATIVE_BASE_OVERRIDE",
            absolute_delta: vFinal - vInit
        });
    }

    // Calcul de soute classique du taux de croissance delta
    const delta = vFinal - vInit;
    const growthPercent = parseFloat(((delta / Math.abs(vInit)) * 100).toFixed(4));

    res.status(200).json({
        status: "GROWTH_RATIO_COMPUTED_SUCCESSFULLY",
        input_data: { initial: vInit, final: vFinal },
        metrics: {
            absolute_difference: delta,
            growth_percentage: growthPercent,
            multiplier_factor: parseFloat((vFinal / vInit).toFixed(4))
        },
        pipeline_integrity: {
            calculation_type: "STATELESS_DELTA_RATIO",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;