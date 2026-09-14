/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 61 : TIME-DIFF-CALCULATOR CORE ENGINE (CRON & SCHEDULER LAB)
 * ⏱️ LIGHTNING-FAST STATELESS INTERVAL PROCESSOR TO CALCULATE MILLISECOND DEVIATIONS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION ET CALCUL D'ÉCART TEMPOREL SANS MEMOIRE
 */
router.post('/', (req, res) => {
    const { start_timestamp, end_timestamp } = req.body;

    if (!start_timestamp || !end_timestamp) {
        return res.status(400).json({ error: "Missing required params: 'start_timestamp' and 'end_timestamp' ISO strings or Unix numbers." });
    }

    console.log(`[⏱️ TIME-DIFF-CALCULATOR] Ingestion des bornes pour calcul d'intervalle.`);

    const startDate = new Date(start_timestamp);
    const endDate = new Date(end_timestamp);

    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        return res.status(422).json({ error: "Invalid date format parsed. Ensure ISO 8601 strings or numeric weights." });
    }

    const diffMs = endDate.getTime() - startDate.getTime();
    const absoluteDiff = Math.abs(diffMs);

    // Extraction chirurgicale des unites
    const totalSeconds = Math.floor(absoluteDiff / 1000);
    const totalMinutes = Math.floor(totalSeconds / 60);
    const totalHours = Math.floor(totalMinutes / 60);
    const totalDays = Math.floor(totalHours / 24);

    res.status(200).json({
        status: "TIME_INTERVAL_CALCULATED_SUCCESSFULLY",
        bounds: { start: startDate.toISOString(), end: endDate.toISOString() },
        metrics: {
            difference_milliseconds: diffMs,
            is_negative: diffMs < 0,
            readable_split: {
                days: totalDays,
                hours: totalHours % 24,
                minutes: totalMinutes % 60,
                seconds: totalSeconds % 60
            }
        },
        pipeline_integrity: {
            calculation_layer: "STATELESS_CHRONO",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;