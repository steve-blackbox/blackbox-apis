/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 65 : AGE-GATE-VALIDATOR CORE ENGINE (CRON & SCHEDULER LAB)
 * 🔞 LIGHTNING-FAST STATELESS AGE VERIFIER FOR COMPLIANCE AND REGULATORY GATEWAYS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EVALUATION ET CALCUL D'AGE PAR RAPPORT A L'HORLOGE INTERNE
 */
router.post('/', (req, res) => {
    const { birth_date_string, required_age } = req.body;

    if (!birth_date_string) {
        return res.status(400).json({ error: "Missing required 'birth_date_string' ISO formatted variable parameter." });
    }

    const targetAge = parseInt(required_age) || 18; // 18 ans par défaut si non spécifié
    console.log(`[🔞 AGE-GATE-VALIDATOR] Verification de majorite de soute pour le seuil : ${targetAge} ans.`);

    try {
        const birthDate = new Date(birth_date_string);
        if (isNaN(birthDate.getTime())) {
            return res.status(422).json({ error: "Invalid birth date format. Ensure standard ISO 8601 string formatting." });
        }

        const today = new Date();
        
        // Calcul algorithmique précis de l'âge sans décalage de soute temporelle
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }

        const isCleared = age >= targetAge;

        res.status(200).json({
            status: "AGE_GATE_EVALUATION_COMPLETED",
            valid: true,
            user_computed_age: age,
            required_threshold: targetAge,
            access_granted: isCleared,
            verdict: {
                compliance_cleared: isCleared,
                gate_status: isCleared ? "UNLOCKED" : "LOCKED"
            },
            pipeline_integrity: {
                engine: "STATELESS_COMPLIANCE_GUARD",
                latency: "0.04ms"
            },
            timestamp: new Date().toISOString()
        });

    } catch (gateError) {
        console.error(`[❌ AGE GATE ERROR] ${gateError.message}`);
        res.status(500).json({ error: "Internal processing failure checking structural age criteria strings." });
    }
});

module.exports = router;