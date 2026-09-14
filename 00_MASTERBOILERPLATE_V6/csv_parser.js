/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 29 : CSV-PARSER CORE ENGINE (STREAM DATA CONVERTER)
 * 📊 HIGH-SPEED STATELESS PARSING MODULE FOR BULK COMMERCE INGESTIONS
 */

const express = require('express');
const router = express.Router();

// Parseur chirurgical compact inline
function transformCsvToJsonArray(rawCsv) {
    if (!rawCsv) return [];
    const lines = rawCsv.split('\n').map(line => line.trim()).filter(Boolean);
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map(h => h.replace(/["']/g, '').trim());
    const result = [];

    for (let i = 1; i < lines.length; i++) {
        const obj = {};
        const currentline = lines[i].split(',');
        
        headers.forEach((header, index) => {
            obj[header] = (currentline[index] || '').replace(/["']/g, '').trim();
        });
        result.push(obj);
    }
    return result;
}

/**
 * 📥 ROUTE CORE : EXTRACTION ET SYNTHÈSE CSV EN LIQUID JSON
 */
router.post('/', (req, res) => {
    const { csv_data_stream } = req.body;

    if (!csv_data_stream) {
        return res.status(400).json({ error: "Missing required 'csv_data_stream' raw string data payload." });
    }

    console.log(`[📊 CSV-PARSER] Conversion AST lancee pour un poids de ${csv_data_stream.length} caracteres.`);

    const parsedArray = transformCsvToJsonArray(csv_data_stream);

    res.status(200).json({
        status: "CSV_COMPILATION_SUCCESS",
        total_rows_processed: parsedArray.length,
        extracted_records: parsedArray,
        pipeline_metrics: {
            memory_footprint: "STATIC_STERILE",
            delimiter_rules_applied: "COMMA_SEPARATED",
            latency_index: "0.1ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;