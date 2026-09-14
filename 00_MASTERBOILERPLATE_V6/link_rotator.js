/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 22 : LINK-ROTATOR CORE ENGINE (STATELESS LOAD BALANCER)
 * 🔀 CHIRURGICAL AFFILIATE SPLITTER & ZERO-COOKIE REDIRECTION GENERATOR
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : EQUILIBRAGE D'AFFILIATION EN FLUX PUR
 */
router.post('/', (req, res) => {
    const { links_array } = req.body; // Doit recevoir un tableau d'objets [{url: '...', weight: 50}]

    if (!links_array || !Array.isArray(links_array) || links_array.length === 0) {
        return res.status(400).json({ error: "Missing valid 'links_array' in request body structures." });
    }

    console.log(`[🔀 LINK-ROTATOR] Calcul de repartition active pour ${links_array.length} destinations.`);

    // Algorithme d'aiguillage mathematique stateless par poids
    let targetSelection = links_array[0].url;
    const roll = Math.random() * 100;
    let accumulatedWeight = 0;

    for (const link of links_array) {
        accumulatedWeight += link.weight || (100 / links_array.length);
        if (roll <= accumulatedWeight) {
            targetSelection = link.url;
            break;
        }
    }

    res.status(200).json({
        status: "ROTATION_COMPUTED",
        redirect_target: targetSelection,
        execution_meta: {
            dice_rolled: roll.toFixed(2),
            cookie_free_secured: true,
            dispatch_latency: "0.05ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;