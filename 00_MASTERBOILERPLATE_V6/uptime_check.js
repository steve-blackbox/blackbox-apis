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
    const { target_url } = req.body;

    if (!target_url) {
        return res.status(400).json({ error: "Missing 'target_url' string parameter." });
    }

    console.log(`[📡 UPTIME-CHECK] Diagnostic lance sur le noeud distant : ${target_url}`);

    const startTime = Date.now();
    let state = "ONLINE";
    let httpCode = 200;

    try {
        const response = await fetch(target_url, { method: 'GET', timeout: 3000 });
        httpCode = response.status;
        if (!response.ok) state = "DEGRADED";
    } catch (err) {
        state = "OFFLINE";
        httpCode = 0;
    }

    const latency = Date.now() - startTime;

    res.status(200).json({
        status: "DIAGNOSTIC_COMPLETED",
        target: target_url,
        node_health: state,
        network_metrics: {
            http_status_code: httpCode,
            response_time_ms: `${latency}ms`,
            clearance: state === "ONLINE" ? "SECURED" : "ALERT_TRIGGERED"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;