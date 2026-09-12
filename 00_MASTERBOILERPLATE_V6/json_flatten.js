const express = require('express');
const router = express.Router();
console.log('[⚙️ ENGINE] Robot 04 JSON-Flatten local worker loaded.');

router.get('/', (req, res) => {
    res.status(200).json({ status: "ACTIVE", robot: "Robot 04 — JSON Flatten" });
});
module.exports = router;