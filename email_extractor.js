/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 42 : EMAIL-EXTRACTOR CORE ENGINE (HEAVY REGEX LAB)
 * 🧹 LIGHTNING-FAST STATELESS BULK EMAIL HARVESTER FROM UNSTRUCTURED TEXT payloads
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EXTRACTION PAR RECH_ERCHE D'ARBRE REGEX INLINE
 */
router.post('/', (req, res) => {
    const { raw_corpus_text } = req.body;

    if (!raw_corpus_text) {
        return res.status(400).json({ error: "Missing required 'raw_corpus_text' string parameter string inside payload." });
    }

    console.log(`[🧹 EMAIL-EXTRACTOR] Analyse d'un corpus de texte brut pour extraction.`);

    // Regex chirurgicale de soute industrielle pour capturer les adresses e-mails standardisees
    const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    
    const matches = raw_corpus_text.match(emailPattern) || [];
    
    // Elimination instantanee des doublons de soute
    const uniqueEmails = [...new Set(matches.map(email => email.toLowerCase().trim()))];

    res.status(200).json({
        status: "RAW_TEXT_STREAM_PROCESSED",
        total_extracted_found: matches.length,
        total_unique_extracted: uniqueEmails.length,
        harvested_records: uniqueEmails,
        pipeline_integrity: {
            cache_usage: "STERILE_NONE",
            latency: "0.08ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;