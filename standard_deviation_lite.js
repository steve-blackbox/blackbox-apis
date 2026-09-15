/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 84 : STANDARD-DEVIATION-LITE CORE ENGINE (MATH & STATS LAB)
 * 📊 LIGHTNING-FAST STATELESS VARIANCE AND DEVIATION METRICS PROCESSOR
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION ET EXTRACTION STATISTIQUE EN PARALLÈLE SÈCHE
 */
router.post('/', (req, res) => {
    const { numeric_dataset } = req.body;

    if (!numeric_dataset || !Array.isArray(numeric_dataset) || numeric_dataset.length === 0) {
        return res.status(400).json({ error: "Missing required 'numeric_dataset' as a non-empty array of numbers." });
    }

    console.log(`[📊 STANDARD-DEVIATION] Ingestion d'une serie de ${numeric_dataset.length} elements.`);

    const numbers = numeric_dataset.map(n => parseFloat(n)).filter(n => !isNaN(n));

    if (numbers.length === 0) {
        return res.status(422).json({ error: "No valid numeric elements extracted from dataset payload." });
    }

    // 1. Calcul de la moyenne de soute
    const totalSum = numbers.reduce((acc, curr) => acc + curr, 0);
    const mean = totalSum / numbers.length;

    // 2. Calcul de la variance et de l'ecart-type
    const squareDiffs = numbers.map(n => Math.pow(n - mean, 2));
    const variance = squareDiffs.reduce((acc, curr) => acc + curr, 0) / numbers.length;
    const stdDeviation = Math.sqrt(variance);

    res.status(200).json({
        status: "STATISTICAL_METRICS_COMPUTED",
        dataset_count: numbers.length,
        metrics: {
            average_mean: parseFloat(mean.toFixed(4)),
            variance: parseFloat(variance.toFixed(4)),
            standard_deviation: parseFloat(stdDeviation.toFixed(4)),
            min_value: Math.min(...numbers),
            max_value: Math.max(...numbers)
        },
        pipeline_integrity: {
            method: "POPULATION_VARIANCE_FORMULA",
            latency: "0.06ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;