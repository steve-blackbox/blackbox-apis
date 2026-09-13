const express = require('express');
const router = express.Router();

console.log('[⚙️ ENGINE] Robot 15 - Mock Generator active.');

router.get('/', (req, res) => {
    res.status(200).json({
        status: "ACTIVE",
        robot: "Robot 15 — Mock Generator",
        message: "Ready to output thousands of fake operational datasets for testing."
    });
});

router.post('/process', async (req, res) => {
    try {
        const { rowsCount } = req.body;
        const requestedRows = rowsCount || 100;
        
        // Le réacteur de génération de fausses données sera injecté ici
        res.status(200).json({ success: true, robot: "Robot 15", generatedRows: requestedRows });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;