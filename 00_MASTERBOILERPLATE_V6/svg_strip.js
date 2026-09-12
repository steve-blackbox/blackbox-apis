const express = require('express');
const router = express.Router();
console.log('[⚙️ ENGINE] Robot 05 SVG-Strip local worker loaded.');

router.get('/', (req, res) => {
    res.status(200).json({ status: "ACTIVE", robot: "Robot 05 — SVG Strip" });
});
module.exports = router;