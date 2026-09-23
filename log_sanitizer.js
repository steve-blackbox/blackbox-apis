/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELATION
 * 🤖 ROBOT 20 : LOG-SANITIZER CORE ENGINE (COMPLIANCE BUFFER)
 * 🧼 AUTOMATED REAL-TIME STRING SCRUBBER FOR GDPR & HIPAA INTEGRITY
 */

const express = require('express');
const router = express.Router();

/** Luhn checksum — filters out plain 13-16 digit runs (order IDs, phone numbers,
 * tracking numbers...) that aren't actually valid card numbers, cutting false positives. */
function passesLuhnCheck(digits) {
    let sum = 0;
    let shouldDouble = false;
    for (let i = digits.length - 1; i >= 0; i--) {
        let d = parseInt(digits[i], 10);
        if (shouldDouble) {
            d *= 2;
            if (d > 9) d -= 9;
        }
        sum += d;
        shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
}

// Filtre regex chirurgical anti-fuite de donnees sensibles
function scrubSensitiveLogs(logStream) {
    if (!logStream) return { output: '', matches: { cards: 0, emails: 0, tokens: 0, ips: 0 } };
    const matches = { cards: 0, emails: 0, tokens: 0, ips: 0 };

    let output = logStream
        // Masquage des numeros de cartes bancaires potentiels — verification Luhn
        // reelle pour eviter de masquer des sequences de chiffres innocentes.
        .replace(/\b(?:\d[ -]*?){13,16}\b/g, (match) => {
            const digitsOnly = match.replace(/[^\d]/g, '');
            if (!passesLuhnCheck(digitsOnly)) return match;
            matches.cards++;
            return '[STRIPPED_CREDIT_CARD]';
        })
        // Masquage des adresses e-mails
        .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, () => { matches.emails++; return '[STRIPPED_EMAIL]'; })
        // Masquage des jetons d'autorisation porteurs (Bearer, API keys, JWT)
        .replace(/(bearer\s+)[A-Za-z0-9\-._~+\/]+=*/gim, (m, p1) => { matches.tokens++; return `${p1}[STRIPPED_TOKEN]`; })
        .replace(/\b(sk_live_|sk_test_|pk_live_|AKIA)[A-Za-z0-9]{10,}\b/g, () => { matches.tokens++; return '[STRIPPED_TOKEN]'; })
        .replace(/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g, () => { matches.tokens++; return '[STRIPPED_JWT]'; })
        // Masquage des adresses IPv4
        .replace(/\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b/g, () => { matches.ips++; return '[STRIPPED_IP]'; });

    return { output, matches };
}

/**
 * 📥 ROUTE CORE : PURGE DE DONNÉES EN FLUX TENDU
 */
router.post('/', (req, res) => {
    const { log_data } = req.body;

    if (!log_data) {
        return res.status(400).json({ error: "Missing required 'log_data' string payload." });
    }

    console.log(`[🧼 LOG-SANITIZER] Filtrage de securite active sur un flux de donnees.`);

    const { output: sanitizedOutput, matches } = scrubSensitiveLogs(log_data);
    const totalMatches = matches.cards + matches.emails + matches.tokens + matches.ips;

    res.status(200).json({
        status: "COMPLIANCE_PURGE_SUCCESS",
        sanitized_log: sanitizedOutput,
        compliance_check: {
            pii_data_scrubbed: totalMatches > 0,
            patterns_found: matches,
            // Factual statement about what this pass did, not a legal certification —
            // actual GDPR/HIPAA compliance depends on your full data pipeline, not
            // a single regex pass.
            scrub_verdict: totalMatches > 0 ? "SENSITIVE_PATTERNS_REDACTED" : "NO_SENSITIVE_PATTERNS_DETECTED"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;