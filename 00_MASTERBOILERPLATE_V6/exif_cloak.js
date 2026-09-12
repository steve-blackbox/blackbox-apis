const express = require('express');
const router = express.Router();
console.log('[⚙️ ENGINE] Robot 02 Exif-Cloak local worker loaded.');

router.get('/', (req, res) => {
    res.status(200).json({ status: "ACTIVE", robot: "Robot 02 — Exif Cloak" });
});
module.exports = router;