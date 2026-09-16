const express = require('express');
const router = express.Router();

router.post('/', (req, res) => {
    const { raw_headers_object } = req.body;
    if (!raw_headers_object || typeof raw_headers_object !== 'object') {
        return res.status(400).json({ error: "Missing or malformed 'raw_headers_object'." });
    }
    
    const headers = {};
    Object.keys(raw_headers_object).forEach(k => { headers[k.toLowerCase()] = raw_headers_object[k]; });

    const auditMap = {
        "strict-transport-security": headers["strict-transport-security"] ? "SECURE_ACTIVE" : "MISSING_LEAK",
        "content-security-policy": headers["content-security-policy"] ? "SECURE_ACTIVE" : "MISSING_LEAK",
        "x-frame-options": headers["x-frame-options"] ? "SECURE_ACTIVE" : "MISSING_LEAK"
    };

    res.status(200).json({
        status: "HTTP_SECURITY_HEADERS_AUDITED",
        audit_matrix: auditMap,
        timestamp: new Date().toISOString()
    });
});

module.exports = router; // <--- LE VERROU OBLIGATOIRE QUI EMPÊCHE LE CRASH !