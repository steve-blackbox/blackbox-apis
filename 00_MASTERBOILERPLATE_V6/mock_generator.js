const express = require('express');
const router = express.Router();
router.post('/', (req, res) => {
    console.log("[🎲 MOCK-GENERATOR] Stream stérile actif.");
    res.status(200).json({ status: "SUCCESS", data: [] });
});
module.exports = router;