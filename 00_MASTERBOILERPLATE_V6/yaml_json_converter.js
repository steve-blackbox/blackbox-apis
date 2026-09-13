const express = require('express');
const router = express.Router();

console.log('[⚙️ ENGINE] Robot 14 - YAML/JSON Converter active.');

router.get('/', (req, res) => {
    res.status(200).json({
        status: "ACTIVE",
        robot: "Robot 14 — YAML JSON Converter",
        message: "Ready to safely translate DevOps architecture registries."
    });
});

router.post('/process', async (req, res) => {
    try {
        const { data, targetFormat } = req.body;
        if (!data || !targetFormat) return res.status(400).json({ error: "Missing core translation payloads" });
        
        // Le réacteur de conversion de fichiers sera injecté ici
        res.status(200).json({ success: true, robot: "Robot 14", convertedData: "Translated configuration stream" });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;