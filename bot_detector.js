/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 33 : BOT-DETECTOR CORE ENGINE (INBOUND AUTOMATION DETECTION)
 * 👁️ REAL-TIME BEHAVIORAL ATTRIBUTE INSPECTION GATEWAY FOR YOUR OWN TRAFFIC
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : VERIFICATION SYNTAXIQUE ET SIGNATURES D'AUTOMATISATION
 */
router.post('/', (req, res) => {
    const { headers_payload, fingerprint_meta } = req.body;

    if (!headers_payload) {
        return res.status(400).json({ error: "Missing required 'headers_payload' object inside dataset request." });
    }

    console.log(`[👁️ BOT-DETECTOR] Analyse d'une nouvelle requete entrante.`);

    const signals = [];
    // Each signal carries its own weight (0-100) reflecting how strongly it alone
    // indicates automation, so the final score reflects the *combination* of
    // evidence rather than a hardcoded number.
    const addSignal = (code, weight) => signals.push({ code, weight });

    // --- Header-based signatures -------------------------------------------------
    const userAgent = (headers_payload['user-agent'] || '').toLowerCase();
    const knownHeadless = ['headless', 'puppeteer', 'playwright', 'phantomjs'];
    const knownCliClients = ['curl/', 'wget/', 'python-requests', 'python-urllib', 'go-http-client', 'axios/', 'okhttp'];
    const knownCrawlers = ['bot', 'crawler', 'spider', 'scrapy', 'httpclient'];

    if (knownHeadless.some(sig => userAgent.includes(sig))) addSignal('HEADLESS_USER_AGENT_SIGNATURE', 70);
    if (knownCliClients.some(sig => userAgent.includes(sig))) addSignal('CLI_HTTP_CLIENT_SIGNATURE', 55);
    if (knownCrawlers.some(sig => userAgent.includes(sig))) addSignal('CRAWLER_SIGNATURE', 60);
    if (!userAgent) addSignal('MISSING_USER_AGENT', 40);

    if (headers_payload['x-selenium-test'] || headers_payload['webdriver']) {
        addSignal('AUTOMATION_DRIVERS_EXPOSED', 80);
    }
    if (!headers_payload['accept-language']) addSignal('MISSING_ACCEPT_LANGUAGE', 15);
    if (!headers_payload['accept']) addSignal('MISSING_ACCEPT_HEADER', 10);

    // --- Client-reported fingerprint signals (fingerprint_meta) -------------------
    // Previously accepted but never inspected — now genuinely factored into the score.
    if (fingerprint_meta && typeof fingerprint_meta === 'object') {
        if (fingerprint_meta.webdriver === true) addSignal('NAVIGATOR_WEBDRIVER_FLAG', 85);
        if (Array.isArray(fingerprint_meta.plugins) && fingerprint_meta.plugins.length === 0) addSignal('ZERO_BROWSER_PLUGINS', 20);
        if (Array.isArray(fingerprint_meta.languages) && fingerprint_meta.languages.length === 0) addSignal('EMPTY_LANGUAGES_LIST', 20);
        if (fingerprint_meta.hardwareConcurrency === 0) addSignal('ZERO_HARDWARE_CONCURRENCY', 15);
        if (fingerprint_meta.hasChrome === false && userAgent.includes('chrome')) addSignal('CHROME_UA_WITHOUT_CHROME_RUNTIME', 30);
    }

    // Combine independent signals: 1 - product(1 - weight) so multiple weak signals
    // stack into a stronger verdict, capped at 99.5% (never claim absolute certainty).
    const combinedProbability = signals.length
        ? 1 - signals.reduce((acc, s) => acc * (1 - s.weight / 100), 1)
        : 0;
    const confidenceScore = Math.min(99.5, combinedProbability * 100);
    const botDetected = confidenceScore >= 50;

    res.status(200).json({
        status: "BEHAVIORAL_AUDIT_COMPLETED",
        automated_traffic_detected: botDetected,
        security_verdict: botDetected ? "DENIED_OR_CHALLENGED" : "CLEAR_HUMAN_PATH",
        diagnostic: {
            flags: signals.map(s => s.code),
            bot_probability_score: `${confidenceScore.toFixed(1)}%`
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;
