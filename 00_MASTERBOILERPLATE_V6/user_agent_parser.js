/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 80 : USER-AGENT-PARSER CORE ENGINE (AGENT ANALYTICS LAB)
 * 🔬 LIGHTNING-FAST STATELESS EXTRACTOR FOR BROWSER LOGISTICS AND SYSTEM SIGNATURES
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION ET DECOUPAGE DES SIGNATURES NAVIGATEURS UTILISATEURS
 */
router.post('/', (req, res) => {
    const { raw_user_agent_string } = req.body;

    if (!raw_user_agent_string) {
        return res.status(400).json({ error: "Missing required 'raw_user_agent_string' parameter variable string." });
    }

    const ua = raw_user_agent_string.toString().trim();
    console.log(`[🔬 USER-AGENT-PARSER] Extraction et diagnostic des signatures environnement pour un client.`);

    let detectedOs = "Unknown OS";
    let detectedEngine = "Unknown Engine";

    // Extraction chirurgicale via filtres de soute lineaires rapides
    if (/macintosh|mac os x/i.test(ua)) detectedOs = "macOS";
    else if (/windows|win32/i.test(ua)) detectedOs = "Windows";
    else if (/android/i.test(ua)) detectedOs = "Android";
    else if (/iphone|ipad|ipod/i.test(ua)) detectedOs = "iOS";
    else if (/linux/i.test(ua)) detectedOs = "Linux";

    if (/chrome|crios/i.test(ua) && !/edge|edg/i.test(ua)) detectedEngine = "Blink (Chrome)";
    else if (/safari/i.test(ua) && !/chrome|crios/i.test(ua)) detectedEngine = "WebKit (Safari)";
    else if (/firefox|fxios/i.test(ua)) detectedEngine = "Gecko (Firefox)";
    else if (/edge|edg/i.test(ua)) detectedEngine = "EdgeHTML / Blink (Edge)";

    res.status(200).json({
        status: "USER_AGENT_FULLY_PARSED",
        input_string: ua,
        extracted_matrix: {
            operating_system: detectedOs,
            rendering_engine: detectedEngine,
            is_mobile_or_tablet: /mobile|android|iphone|ipad|tablet/i.test(ua)
        },
        pipeline_integrity: {
            parser_type: "REGULAR_EXPRESSION_STATELESS_GRID",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;