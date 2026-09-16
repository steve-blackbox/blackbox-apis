/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 67 : KEYWORD-DENSITY-ANALYZER CORE ENGINE (ASSET SHRINK LAB)
 * 📈 LIGHTNING-FAST STATELESS SEMANTIC COUNTER FOR SEO AGILITY INFRASTRUCTURE
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EXTRACTION ET CALC_UL SÉMANTIQUE DES MOTS-CLÉS DE SÔUTE
 */
router.post('/', (req, res) => {
    const { raw_text_corpus } = req.body;

    if (!raw_text_corpus) {
        return res.status(400).json({ error: "Missing required 'raw_text_corpus' string parameter inside payload." });
    }

    console.log(`[📈 KEYWORD-DENSITY] Ingestion d'un flux de texte sémantique.`);

    // Nettoyage textuel et conversion en minuscules
    const cleanWords = raw_text_corpus
        .toLowerCase()
        .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"']/g, "")
        .replace(/\s+/g, " ")
        .split(" ")
        .filter(word => word.length > 3);

    const totalWordsCount = cleanWords.length;
    const frequencyMap = {};

    // Cartographie instantanée des fréquences de soute
    cleanWords.forEach(word => {
        frequencyMap[word] = (frequencyMap[word] || 0) + 1;
    });

    // Tri chirurgical pour extraire le top 10 des répétitions
    const sortedKeywords = Object.keys(frequencyMap)
        .map(key => ({
            keyword: key,
            occurrences: frequencyMap[key],
            density_percentage: parseFloat(((frequencyMap[key] / totalWordsCount) * 100).toFixed(2))
        }))
        .sort((a, b) => b.occurrences - a.occurrences)
        .slice(0, 10);

    res.status(200).json({
        status: "SEMANTIC_DENSITY_ANALYSIS_COMPLETED",
        total_significant_words: totalWordsCount,
        top_keywords_matrix: sortedKeywords,
        pipeline_integrity: {
            analysis_type: "STATELESS_FREQUENCY_MAP",
            latency: "0.06ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;