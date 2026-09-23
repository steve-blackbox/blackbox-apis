/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELATION
 * 🤖 ROBOT 19 : UPTIME-CHECK CORE ENGINE (STATELESS CLUSTER DIAGNOSTIC)
 * 📡 ULTRA-FAST TCP HANDSHAKE MONITOR & ENDPOINT DECAY DETECTOR
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : PING & AUDIT SANS MEMOIRE
 */
router.post('/', async (req, res) => {
    const { target_url, timeout_ms } = req.body;

    if (!target_url) {
        return res.status(400).json({ error: "Missing 'target_url' string parameter." });
    }

    let parsedUrl;
    try {
        parsedUrl = new URL(target_url);
    } catch (e) {
        return res.status(400).json({ error: "Invalid 'target_url': must be a well-formed absolute URL." });
    }
    if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:') {
        return res.status(400).json({ error: "Invalid 'target_url': only http:// and https:// protocols are supported." });
    }

    // Real enforced timeout via AbortController — native fetch() silently ignores a
    // plain `timeout` option, so without this an unresponsive target could hang the
    // request far longer than the value implied by the response.
    const boundedTimeout = Math.min(Math.max(parseInt(timeout_ms, 10) || 3000, 500), 15000);

    console.log(`[📡 UPTIME-CHECK] Diagnostic lance sur le noeud distant : ${target_url}`);

    const startTime = Date.now();
    let state = "ONLINE";
    let httpCode = 200;
    let failureReason = null;

    const controller = new AbortController();
    const abortTimer = setTimeout(() => controller.abort(), boundedTimeout);

    try {
        const response = await fetch(parsedUrl.toString(), { method: 'GET', signal: controller.signal });
        httpCode = response.status;
        if (!response.ok) state = "DEGRADED";
    } catch (err) {
        state = "OFFLINE";
        httpCode = 0;
        failureReason = err.name === 'AbortError'
            ? `TIMEOUT_EXCEEDED_${boundedTimeout}MS`
            : (err.cause?.code || err.code || 'CONNECTION_FAILED');
    } finally {
        clearTimeout(abortTimer);
    }

    const latency = Date.now() - startTime;

    res.status(200).json({
        status: "DIAGNOSTIC_COMPLETED",
        target: target_url,
        node_health: state,
        network_metrics: {
            http_status_code: httpCode,
            response_time_ms: latency,
            timeout_budget_ms: boundedTimeout,
            failure_reason: failureReason,
            clearance: state === "ONLINE" ? "SECURED" : "ALERT_TRIGGERED"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;