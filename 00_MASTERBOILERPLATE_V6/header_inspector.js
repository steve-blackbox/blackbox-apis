/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 50 : HEADER-INSPECTOR CORE ENGINE (CYBER-DEFENSE NODES)
 * 🌐 STATELESS SECURITY HEADER AUDITOR TO DETECT CSP & HSTS PROTECTION LEAKS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION SYNTAXIQUE DES EN-TÊTES DE SÔUTE
 */
router.post('/', (req, res) => {
    const { raw_headers_object } = req.body;

    if (!raw_headers_object || typeof raw_headers_object !== 'object') {
        return res.status(400).json({ error: "Missing required 'raw_headers_object' key-value mapping string." });
    }

    console.log(`[🌐 HEADER-INSPECTOR] Lancement de l'audit de soute pour un nouvel ensemble d'en-tetes.`);

    const headers = {};
    Object.keys(raw_headers_object).forEach(k => {
        headers[k.toLowerCase()] = raw_headers_object[k];
    });

    // Verification clinique de l'arsenal Securite Reseau
    const auditMap = {
        "strict-transport-security": headers["strict-transport-security"] ? "SECURE_ACTIVE" : "MISSING_LEAK",
        "content-security-policy": headers["content-security-policy"] ? "SECURE_ACTIVE" : "MISSING_LEAK",
        "x-frame-options": headers["x-frame-options"] ? "SECURE_ACTIVE" : "MISSING_LEAK",
        "x-content-type-options": headers["x-content-type-options"] ? "SECURE_ACTIVE" : "MISSING_LEAK"
    };

    const leaksFound = Object.values(auditMap).filter(v => v === "MISSING_LEAK").length;

    res.status(200).json({
        status: "HTTP_SECURITY_HEADERS_AUDITED",
        total_security_headers_checked: Object.keys(auditMap).length,
        vulnerabilities_detected: leaksFound,
        audit_matrix: auditMap,
        verdict: {
            infrastructure_hardened: leaksFound === 0,
            risk_score: leaksFound * 25
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;