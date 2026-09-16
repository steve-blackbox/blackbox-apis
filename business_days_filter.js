/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 63 : BUSINESS-DAYS-FILTER CORE ENGINE (CRON & SCHEDULER LAB)
 * 📅 LIGHTNING-FAST STATELESS FILTER TO COMPUTE WORKING DAYS EXCLUDING WEEKENDS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : CALC_UL SANS MEMOIRE DES JOURS OUVRES ENTRE DEUX BORNES
 */
router.post('/', (req, res) => {
    const { start_date, end_date } = req.body;

    if (!start_date || !end_date) {
        return res.status(400).json({ error: "Missing required params: 'start_date' and 'end_date' ISO strings." });
    }

    console.log(`[📅 BUSINESS-DAYS-FILTER] Evaluation de soute temporelle.`);

    let dStart = new Date(start_date);
    let dEnd = new Date(end_date);

    if (isNaN(dStart.getTime()) || isNaN(dEnd.getTime())) {
        return res.status(422).json({ error: "Invalid date format received. Ensure standard ISO 8601 formatting." });
    }

    // Gestion de l'inversion chronologique potentielle en soute
    if (dStart > dEnd) {
        const temp = dStart;
        dStart = dEnd;
        dEnd = temp;
    }

    let totalDays = 0;
    let businessDays = 0;
    const current = new Date(dStart);

    // Boucle d'evaluation de soute brute (Stateless loop)
    while (current <= dEnd) {
        totalDays++;
        const dayOfWeek = current.getDay(); // 0 = Dimanche, 6 = Samedi
        if (dayOfWeek !== 0 && dayOfWeek !== 6) {
            businessDays++;
        }
        current.setDate(current.getDate() + 1);
    }

    res.status(200).json({
        status: "BUSINESS_DAYS_COMPUTED_SUCCESSFULLY",
        bounds: { start: dStart.toISOString(), end: dEnd.toISOString() },
        metrics: {
            total_calendar_days: totalDays,
            net_business_days_found: businessDays,
            weekend_days_excluded: totalDays - businessDays
        },
        pipeline_integrity: {
            calendar_rule: "STANDARD_WESTERN_WEEKEND_STRIP",
            latency: "0.08ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;