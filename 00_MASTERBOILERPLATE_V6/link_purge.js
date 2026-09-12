const express = require('express');
const router = express.Router();
console.log('[⚙️ ENGINE] Robot 03 Link-Purge local worker loaded.');

router.get('/', (req, res) => {
    res.status(200).json({ status: "ACTIVE", robot: "Robot 03 — Link Purge" });
});
module.exports = router;