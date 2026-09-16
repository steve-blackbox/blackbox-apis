/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 32 : TEXT-EXTRACTOR CORE ENGINE (DOM TEXT HARVESTER)
 * 🧹 STATELESS HTML CLEANER TO PREPARE UNBIASED DATA PAYLOADS FOR LLM DATA FLOWS
 */

const express = require('express');
const router = express.Router();

// Fonction chirurgicale de soute pour isoler le texte pur
function extractPureText(htmlString) {
    if (!htmlString) return '';
    return htmlString
        .replace(/<script[\s\S]*?<\/script>/gim, '') // Elimine completement les balises scripts
        .replace(/<style[\s\S]*?<\/style>/gim, '')   // Elimine completement les balises CSS sheets
        .replace(/<[^>]*>/g, ' ')                    // Detruit toutes les balises HTML restantes
        .replace(/\s+/g, ' ')                        // Supprime les espaces et sauts de ligne multiples
        .trim();
}

/**
 * 📥 ROUTE CORE : HARVESTING TEXTUEL PARFAIT
 */
router.post('/', (req, res) => {
    const { html_source } = req.body;

    if (!html_source) {
        return res.status(400).json({ error: "Missing required 'html_source' markup string payload." });
    }

    console.log(`[🧹 TEXT-EXTRACTOR] Nettoyage DOM lance pour un flux de ${html_source.length} caracteres.`);

    const pureText = extractPureText(html_source);

    res.status(200).json({
        status: "TEXT_EXTRACTION_SUCCESS",
        extracted_text: pureText,
        metrics: {
            input_length: html_source.length,
            output_length: pureText.length,
            token_reduction_ratio: `${((1 - (pureText.length / html_source.length)) * 100).toFixed(1)}% avoided`,
            isolation_state: "STERILE"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;