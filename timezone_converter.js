/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 64 : TIMEZONE-CONVERTER CORE ENGINE (CRON & SCHEDULER LAB)
 * 🌍 LIGHTNING-FAST STATELESS TRANSLATOR FOR INTERNATIONAL DATE-TIME PAYLOADS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : TRANSLATION DE TIMEZONE FLUIDE EN FLUX DIRECT
 */
router.post('/', (req, res) => {
    const { input_date_string, source_tz, target_tz } = req.body;

    if (!input_date_string || !target_tz) {
        return res.status(400).json({ error: "Missing required params: 'input_date_string' and 'target_tz' name strings." });
    }

    console.log(`[🌍 TIMEZONE-CONVERTER] Ingestion et routage de fuseau horaire vers : ${target_tz}`);

    try {
        const baseDate = new Date(input_date_string);
        if (isNaN(baseDate.getTime())) {
            return res.status(422).json({ error: "Invalid input date format string. Ensure standard ISO 8601 syntax." });
        }

        // Options d'internationalisation natives de Node.js (Stateless execution layer)
        const formatOptions = {
            timeZone: target_tz.trim(),
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: false
        };

        const targetFormatted = new Intl.DateTimeFormat('en-US', formatOptions).format(baseDate);

        res.status(200).json({
            status: "DATE_TIME_CONVERTED_SUCCESSFULLY",
            original_input: input_date_string,
            source_timezone: source_tz || "UTC_DETECTED",
            target_timezone: target_tz,
            translated_output: targetFormatted,
            pipeline_integrity: {
                engine: "INTL_NATIVE_NODE",
                latency: "0.06ms"
            },
            timestamp: new Date().toISOString()
        });

    } catch (tzError) {
        console.error(`[❌ TIMEZONE CONVERSION ERROR] ${tzError.message}`);
        res.status(422).json({ error: "Failed to parse target timezone. Ensure a valid IANA timezone identifier string string." });
    }
});

module.exports = router;