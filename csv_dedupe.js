const express = require('express');
const router = express.Router();

console.log('[⚙️ ENGINE] Robot 13 - CSV Dedupe active.');

/**
 * Parses raw CSV text into an array of rows (array of string fields),
 * handling quoted fields with embedded commas, newlines, and escaped quotes ("").
 */
function parseCSV(csvText) {
    const rows = [];
    let row = [];
    let field = '';
    let inQuotes = false;

    for (let i = 0; i < csvText.length; i++) {
        const char = csvText[i];
        const next = csvText[i + 1];

        if (inQuotes) {
            if (char === '"' && next === '"') {
                field += '"';
                i++;
            } else if (char === '"') {
                inQuotes = false;
            } else {
                field += char;
            }
        } else {
            if (char === '"') {
                inQuotes = true;
            } else if (char === ',') {
                row.push(field);
                field = '';
            } else if (char === '\r') {
                // ignore, handled by \n
            } else if (char === '\n') {
                row.push(field);
                rows.push(row);
                row = [];
                field = '';
            } else {
                field += char;
            }
        }
    }

    if (field.length > 0 || row.length > 0) {
        row.push(field);
        rows.push(row);
    }

    // Drop trailing fully-empty rows caused by a final newline
    return rows.filter(r => !(r.length === 1 && r[0] === ''));
}

function escapeCSVField(value) {
    const str = String(value ?? '');
    if (/[",\n]/.test(str)) {
        return '"' + str.replace(/"/g, '""') + '"';
    }
    return str;
}

function toCSV(rows) {
    return rows.map(r => r.map(escapeCSVField).join(',')).join('\n');
}

router.get('/', (req, res) => {
    res.status(200).json({
        status: "ACTIVE",
        robot: "Robot 13 — CSV Dedupe",
        message: "Ready to ingest heavy lead files and purge duplicates smoothly."
    });
});

router.post('/process', async (req, res) => {
    try {
        const { csvRaw, hasHeader = true, dedupeColumns } = req.body;
        if (!csvRaw || typeof csvRaw !== 'string' || !csvRaw.trim()) {
            return res.status(400).json({ error: "Missing CSV raw string payload" });
        }

        const allRows = parseCSV(csvRaw.trim());
        if (allRows.length === 0) {
            return res.status(200).json({
                status: "CSV_DEDUPLICATION_COMPLETE",
                total_input_rows: 0,
                duplicates_removed: 0,
                unique_rows_kept: 0,
                cleaned_csv: ""
            });
        }

        let header = null;
        let dataRows = allRows;
        if (hasHeader) {
            header = allRows[0];
            dataRows = allRows.slice(1);
        }

        // Optional: dedupe by specific column names (requires a header row).
        // Falls back to comparing the full row when no columns are specified.
        let keyIndexes = null;
        if (Array.isArray(dedupeColumns) && dedupeColumns.length > 0 && header) {
            keyIndexes = dedupeColumns
                .map(name => header.indexOf(name))
                .filter(idx => idx !== -1);
        }

        const seen = new Set();
        const deduped = [];
        let duplicatesRemoved = 0;

        for (const row of dataRows) {
            const key = (keyIndexes && keyIndexes.length > 0)
                ? keyIndexes.map(idx => (row[idx] ?? '').trim().toLowerCase()).join('||')
                : row.map(v => (v ?? '').trim().toLowerCase()).join('||');

            if (seen.has(key)) {
                duplicatesRemoved++;
                continue;
            }
            seen.add(key);
            deduped.push(row);
        }

        const outputRows = header ? [header, ...deduped] : deduped;

        res.status(200).json({
            status: "CSV_DEDUPLICATION_COMPLETE",
            total_input_rows: dataRows.length,
            duplicates_removed: duplicatesRemoved,
            unique_rows_kept: deduped.length,
            cleaned_csv: toCSV(outputRows)
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
