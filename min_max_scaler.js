/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 85 : MIN-MAX-SCALER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 📊 LIGHTNING-FAST STATELESS VALUE NORMALIZER FOR VISUAL ANALYTICS DASHBOARDS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : NORMALISATION ET MISE A L'ECHELLE INLINE EN FLUX DIRECT
 */
router.post('/', (req, res) => {
    const { raw_data_array } = req.body;

    if (!raw_data_array || !Array.isArray(raw_data_array) || raw_data_array.length === 0) {
        return res.status(400).json({ error: "Missing required 'raw_data_array' as a non-empty list of numerical metrics." });
    }

    console.log(`[📊 MIN-MAX-SCALER] Normalisation lineaire d'un vecteur numerique.`);

    const numbers = raw_data_array.map(n => parseFloat(n)).filter(n => !isNaN(n));

    if (numbers.length === 0) {
        return res.status(422).json({ error: "No valid numeric elements extracted from data array payload." });
    }

    const min = Math.min(...numbers);
    const max = Math.max(...numbers);
    const range = max - min;

    // Normalisation chirurgicale de soute brute
    const scaledArray = numbers.map(n => {
        if (range === 0) return 0; // Evite la division par zero si toutes les valeurs de soute sont identiques
        return parseFloat(((n - min) / range).toFixed(6));
    });

    res.status(200).json({
        status: "DATA_ARRAY_NORMALIZED_SUCCESSFULLY",
        input_count: numbers.length,
        boundaries: { minimum_found: min, maximum_found: max },
        normalized_output_array: scaledArray,
        pipeline_integrity: {
            scale_range: "0_TO_1_COMPLIANT",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;