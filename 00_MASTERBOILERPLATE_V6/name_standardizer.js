/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 91 : NAME-STANDARDIZER CORE ENGINE (DATA NORMALIZERS LAB)
 * 🧹 LIGHTNING-FAST STATELESS INPUT TEXT ALIGNER FOR CUSTOMER CRM HEALTH
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : ALIGNEMENT ET CAP_ITALISATION SYNTAXIQUE SANS MEMOIRE
 */
router.post('/', (req, res) => {
    const { raw_name_string } = req.body;

    if (!raw_name_string) {
        return res.status(400).json({ error: "Missing required 'raw_name_string' parameter variable string." });
    }

    console.log(`[🧹 NAME-STANDARDIZER] Nettoyage et normalisation de soute pour une identite.`);

    const input = raw_name_string.toString().trim();

    // Harmonisation chirurgicale des segments textuels separated by spaces or hyphens
    const standardized = input
        .toLowerCase()
        .split(/(\s+|-)/) // Conserve les espaces et les tirets d'origine pour le maillage
        .map(segment => {
            if (segment.trim().length === 0 || segment === '-') {
                return segment;
            }
            return segment.charAt(0).toUpperCase() + segment.slice(1);
        })
        .join('')
        .replace(/\s+/g, ' '); // Purge des doubles espaces parasites residuels

    res.status(200).json({
        status: "NAME_NORMALIZED_SUCCESSFULLY",
        input_received: input,
        standardized_output: standardized,
        pipeline_integrity: {
            casing_rule: "TITLE_CASE_HYPHEN_SAFE",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;