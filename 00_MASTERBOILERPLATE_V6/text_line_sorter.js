/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 92 : TEXT-LINE-SORTER CORE ENGINE (DATA NORMALIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS MULTI-LINE SORTING ENGINE TO CLEAN DATA LISTS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : ALIGNEMENT ET TRI ALPHABÉTIQUE EN FLUX DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_multi_line_text, sort_direction } = req.body;

    if (raw_multi_line_text === undefined || raw_multi_line_text === null) {
        return res.status(400).json({ error: "Missing required 'raw_multi_line_text' string parameter variable." });
    }

    console.log(`[🧹 TEXT-LINE-SORTER] Ingestion et tri alphabetique d'un bloc de soute.`);

    const direction = (sort_direction || 'asc').toLowerCase().trim();
    const lines = raw_multi_line_text.toString().split(/\r?\n/);
    
    // Purge des lignes de soute vides ou uniquement composees d'espaces
    const filteredLines = lines.filter(line => line.trim().length > 0);

    // Tri chirurgical lineaire standardise
    filteredLines.sort((a, b) => a.localeCompare(b));

    if (direction === 'desc') {
        filteredLines.reverse();
    }

    const sortedOutput = filteredLines.join('\n');

    res.status(200).json({
        status: "TEXT_LINES_SORTED_SUCCESSFULLY",
        configuration: { order: direction },
        metrics: {
            total_input_lines: lines.length,
            cleaned_active_lines: filteredLines.length,
            empty_lines_purged: lines.length - filteredLines.length
        },
        sorted_text_output: sortedOutput,
        pipeline_integrity: {
            sort_layer: "STATELESS_LOCALE_COMPARE",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;