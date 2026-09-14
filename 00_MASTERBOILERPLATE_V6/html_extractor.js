const express = require('express');
const router = express.Router();
router.post('/', (req, res) => {
    console.log("[📡 HTML-EXTRACTOR] Ingestion active.");
    res.status(200).json({ status: "SUCCESS" });
});
module.exports = router;