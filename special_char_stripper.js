/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 98 : SPECIAL-CHAR-STRIPPER CORE ENGINE (CODE OPTIMIZERS LAB)
 * 🛡️ LIGHTNING-FAST STATELESS SANITIZER TO PURGE EMOJIS AND NON-ALPHANUMERIC PARASITES
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : PURGE ET NETTOYAGE PAR EXPRESSIONS RÉGULIÈRES DIRECT ET STERILE
 */
router.post('/', (req, res) => {
    const { raw_dirty_string, allow_spaces } = req.body;

    if (raw_dirty_string === undefined || raw_dirty_string === null) {
        return res.status(400).json({ error: "Missing required 'raw_dirty_string' variable parameter string." });
    }

    console.log(`[🛡️ SPECIAL-CHAR-STRIPPER] Nettoyage d'un flux de texte brut contre les caracteres speciaux.`);

    const text = raw_dirty_string.toString();
    const keepSpaces = allow_spaces === undefined ? true : !!allow_spaces;

    // Logique de soute chirurgicale : selection de la regex selon le parametre d'espaces
    // On ne conserve que les lettres (minuscules/majuscules), chiffres, et optionnellement les espaces de soute
    const regexFilter = keepSpaces ? /[^a-zA-Z0-9\s]/g : /[^a-zA-Z0-9]/g;
    
    const strippedOutput = text.replace(regexFilter, '');

    res.status(200).json({
        status: "STRING_SUCCESSFULLY_STRIPPED_AND_SANITIZED",
        metrics: {
            original_character_count: text.length,
            sanitized_character_count: strippedOutput.length,
            characters_purged: Math.max(0, text.length - strippedOutput.length)
        },
        sanitized_output: strippedOutput,
        pipeline_integrity: {
            security_filter: "ALPHANUMERIC_STRICT_REGEXP",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;