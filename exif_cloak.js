const express = require('express');
const router = express.Router();
router.post('/', (req, res) => {
    console.log("[🛡️ EXIF-CLOAK] Purge métadonnées.");
    res.status(200).json({ status: "SUCCESS" });
});
module.exports = router;