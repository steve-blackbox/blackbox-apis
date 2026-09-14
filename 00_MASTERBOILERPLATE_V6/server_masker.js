const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : OBFUSCATION ET NETTOYAGE DES SIGNATURES SERVEUR
 */
router.post('/', (req, res) => {
    const { raw_headers_input } = req.body;

    if (!raw_headers_input || typeof raw_headers_input !== 'object') {
        return res.status(400).json({ error: "Missing required 'raw_headers_input' object." });
    }

    console.log(`[🎭 SERVER-MASKER] Nettoyage des en-tetes serveurs actif.`);

    const cleanedHeaders = { ...raw_headers_input };
    const headersToMask = ['x-powered-by', 'server', 'x-aspnet-version', 'x-runtime'];
    let mutationsCount = 0;

    Object.keys(cleanedHeaders).forEach(key => {
        if (headersToMask.includes(key.toLowerCase())) {
            cleanedHeaders[key] = "Sovereign-Matrix-Node";
            mutationsCount++;
        }
    });

    res.status(200).json({
        status: "SERVER_SIGNATURES_SUCCESSFULLY_MASKED",
        headers_mutated: mutationsCount,
        sanitized_headers_payload: cleanedHeaders,
        timestamp: new Date().toISOString()
    });
});

module.exports = router; // Existant et scellé au châssis !
