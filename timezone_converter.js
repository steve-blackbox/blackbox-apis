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

    const startTime = process.hrtime.bigint();

    try {
        // Validate target_tz early via Intl (throws RangeError on unknown IANA id).
        new Intl.DateTimeFormat('en-US', { timeZone: target_tz.trim() });

        // Does the input string already carry an explicit UTC offset or 'Z'?
        // e.g. "2024-01-01T12:00:00Z" or "...+02:00" — unambiguous, parse as-is.
        const hasExplicitOffset = /(Z|[+-]\d{2}:?\d{2})$/.test(input_date_string.trim());

        let baseDate;
        let resolvedSourceTz;

        if (hasExplicitOffset || !source_tz) {
            baseDate = new Date(input_date_string);
            resolvedSourceTz = hasExplicitOffset ? "EXPLICIT_OFFSET_IN_INPUT" : "UTC_DETECTED";
        } else {
            // Naive datetime string ("2024-01-01 12:00:00") + an explicit source_tz:
            // interpret those wall-clock digits as local time IN source_tz, not UTC.
            // Previously source_tz was accepted but silently ignored — this now
            // genuinely offsets the parse using the source timezone's real UTC offset.
            new Intl.DateTimeFormat('en-US', { timeZone: source_tz.trim() }); // validates source_tz too

            const naiveUtcGuess = new Date(input_date_string.replace(' ', 'T') + 'Z');
            if (isNaN(naiveUtcGuess.getTime())) {
                return res.status(422).json({ error: "Invalid input date format string. Ensure standard ISO 8601 syntax." });
            }

            // Find the source timezone's offset (in minutes) at that instant, then
            // shift the naive-as-UTC guess back by that offset to get the real UTC instant.
            const tzFormatter = new Intl.DateTimeFormat('en-US', {
                timeZone: source_tz.trim(), hourCycle: 'h23',
                year: 'numeric', month: '2-digit', day: '2-digit',
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
            const parts = Object.fromEntries(tzFormatter.formatToParts(naiveUtcGuess).map(p => [p.type, p.value]));
            const asIfUtc = Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second);
            const offsetMs = asIfUtc - naiveUtcGuess.getTime();
            baseDate = new Date(naiveUtcGuess.getTime() - offsetMs);
            resolvedSourceTz = source_tz.trim();
        }

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
        const elapsedMs = Number(process.hrtime.bigint() - startTime) / 1e6;

        res.status(200).json({
            status: "DATE_TIME_CONVERTED_SUCCESSFULLY",
            original_input: input_date_string,
            source_timezone: resolvedSourceTz,
            target_timezone: target_tz,
            translated_output: targetFormatted,
            pipeline_integrity: {
                engine: "INTL_NATIVE_NODE",
                latency_ms: Number(elapsedMs.toFixed(3))
            },
            timestamp: new Date().toISOString()
        });

    } catch (tzError) {
        console.error(`[❌ TIMEZONE CONVERSION ERROR] ${tzError.message}`);
        res.status(422).json({ error: "Failed to parse source or target timezone. Ensure valid IANA timezone identifier strings." });
    }
});

module.exports = router;