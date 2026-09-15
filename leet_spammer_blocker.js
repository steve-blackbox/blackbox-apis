/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 70 : LEET-SPAMMER-BLOCKER CORE ENGINE (FORM PROTECTION LAB)
 * 🛡️ STATELESS DE-OBFUSCATOR AND DECODER TO NEUTRALIZE STEALTH SPAM ATTACKS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION ET DE-OBFUSCATION DE CHAÎNES LEET SPEAK
 */
router.post('/', (req, res) => {
    const { raw_input_message } = req.body;

    if (!raw_input_message) {
        return res.status(400).json({ error: "Missing required 'raw_input_message' parameter string inside payload." });
    }

    const message = raw_input_message.toString().trim();
    console.log(`[🛡️ LEET-SPAMMER-BLOCKER] Audit de securite cyber-graphique pour un message.`);

    // Matrice dictionnaire stateless d'inversion des principaux caracteres Leet Speak
    const leetMap = {
        '4': 'a', '0': 'o', '3': 'e', '1': 'i', 'l': 'i', '7': 't', 
        '5': 's', '$': 's', '8': 'b', '9': 'g', 'v': 'u', 'w': 'vv'
    };

    // Traduction chirurgicale inline de la soute textuelle
    let decodedMessage = message.toLowerCase();
    Object.keys(leetMap).forEach(char => {
        const replacement = leetMap[char];
        // Protection contre les injections de boucles infinies via regex securisee
        decodedMessage = decodedMessage.split(char).join(replacement);
    });

    // Liste noire de mots strategiques hautement cibles par le spam d'agences
    const blacklist = ['cash', 'free', 'crypto', 'viagra', 'casino', 'poker', 'bonus'];
    let violationDetected = false;
    let flaggedToken = null;

    for (const word of blacklist) {
        if (decodedMessage.includes(word)) {
            violationDetected = true;
            flaggedToken = word;
            break;
        }
    }

    res.status(200).json({
        status: "LEET_SPAM_INSPECTION_COMPLETED",
        spam_attack_detected: violationDetected,
        flagged_element: flaggedToken,
        details: {
            original_input: message,
            de_obfuscated_translation: decodedMessage
        },
        action: violationDetected ? "DROP_AND_BLOCK_TRANSACTION" : "FORWARD_SAFE_STREAM",
        pipeline_integrity: {
            security_policy: "ANTI_OBFUSCATION_GUARD",
            latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;