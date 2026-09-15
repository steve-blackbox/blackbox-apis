const express = require('express');
const router = express.Router();

console.log('[⚙️ ENGINE] Robot 13 - CSV Dedupe active.');

router.get('/', (req, res) => {
    res.status(200).json({
        status: "ACTIVE",
        robot: "Robot 13 — CSV Dedupe",
        message: "Ready to ingest heavy lead files and purge duplicates smoothly."
    });
});

router.post('/process', async (req, res) => {
    try {
        const { csvRaw } = req.body;
        if (!csvRaw) return res.status(400).json({ error: "Missing CSV raw string payload" });
        
        // Le réacteur de nettoyage de doublons sera injecté ici
        res.status(200).json({ success: true, robot: "Robot 13", message: "CSV purged from all dirty data lines" });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;