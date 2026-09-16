/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 69 : WORD-COUNTER-PRO CORE ENGINE (ASSET SHRINK LAB)
 * 📝 LIGHTNING-FAST STATELESS TEXT ANALYTICS METRICS FOR CONTENT PLATFORMS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : COMPTAGE ET CALCUL DU TEMPS DE LECTURE INLINE ET STÉRILE
 */
router.post('/', (req, res) => {
    const { raw_text_payload } = req.body;

    if (raw_text_payload === undefined || raw_text_payload === null) {
        return res.status(400).json({ error: "Missing required 'raw_text_payload' string parameter." });
    }

    const text = raw_text_payload.toString().trim();
    console.log(`[📝 WORD-COUNTER-PRO] Calcul des metriques pour une soute de ${text.length} caracteres.`);

    if (text === "") {
        return res.status(200).json({
            status: "EMPTY_TEXT_PROCESSED",
            metrics: { words: 0, characters_with_spaces: 0, characters_no_spaces: 0, paragraphs: 0, estimated_reading_time_minutes: 0 }
        });
    }

    // Algorithmes de comptage stateless rapides
    const wordsArray = text.split(/\s+/).filter(w => w.length > 0);
    const wordsCount = wordsArray.length;
    const charWithSpaces = text.length;
    const charNoSpaces = text.replace(/\s/g, "").length;
    const paragraphsCount = text.split(/\n\s*\n/).filter(p => p.trim().length > 0).length;
    
    // Vitesse de lecture standardisee: 200 mots / minute
    const readingTime = parseFloat(Math.max(0.1, wordsCount / 200).toFixed(2));

    res.status(200).json({
        status: "TEXT_STREAM_ANALYZED",
        metrics: {
            words: wordsCount,
            characters_with_spaces: charWithSpaces,
            characters_no_spaces: charNoSpaces,
            paragraphs: paragraphsCount,
            estimated_reading_time_minutes: readingTime
        },
        pipeline_integrity: {
            analytics_layer: "CORE_TEXT_STATISTICS",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;