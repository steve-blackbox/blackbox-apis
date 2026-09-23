/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 78 : IP-ANONYMIZER CORE ENGINE (GDPR/RGPD COMPLIANCE LAB)
 * 🛡️ STATELESS IP MASKER FOR ANALYTICS PRIVACY COMPLIANCE (SAME TECHNIQUE AS GOOGLE ANALYTICS' anonymizeIp)
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : MASQUAGE ET ANONYMISATION DE COMPOSANTS RÈSEAU INLINE
 */
router.post('/', (req, res) => {
    const { raw_ip_address } = req.body;

    if (!raw_ip_address) {
        return res.status(400).json({ error: "Missing required 'raw_ip_address' parameter string inside payload." });
    }

    const startTime = process.hrtime.bigint();
    const ip = raw_ip_address.trim();
    console.log(`[🛡️ IP-ANONYMIZER] Application des masques d'anonymisation pour l'adresse reseau.`);

    let anonymizedIp = '';
    let ipVersion = '';

    if (ip.includes('.') && !ip.includes(':')) {
        // Traitement chirurgical de la structure IPv4 (Mise à zéro du dernier octet)
        // — validation stricte de la plage 0-255 par octet, pas juste le nombre de segments.
        ipVersion = 'IPv4';
        const segments = ip.split('.');
        const isValidIPv4 = segments.length === 4 && segments.every(seg => /^\d{1,3}$/.test(seg) && Number(seg) <= 255);
        if (isValidIPv4) {
            segments[3] = '0';
            anonymizedIp = segments.join('.');
        } else {
            return res.status(422).json({ error: "Invalid IPv4 structure: each octet must be a number between 0 and 255." });
        }
    } else if (ip.includes(':')) {
        // Traitement chirurgical de la structure IPv6 (Mise à zéro des derniers blocs)
        // — expansion correcte de la notation compressée "::" avant le masquage,
        // ce qui manquait auparavant (un simple split(':') casse sur ces adresses).
        ipVersion = 'IPv6';
        try {
            const fullGroups = expandIPv6(ip);
            anonymizedIp = `${fullGroups[0]}:${fullGroups[1]}:${fullGroups[2]}:0000:0000:0000:0000:0000`;
        } catch (e) {
            return res.status(422).json({ error: `Invalid IPv6 structure: ${e.message}` });
        }
    } else {
        return res.status(422).json({ error: "Unsupported or non-compliant IP address protocol layout footprint." });
    }

    const elapsedMs = Number(process.hrtime.bigint() - startTime) / 1e6;

    res.status(200).json({
        status: "IP_ADDRESS_ANONYMIZED_SUCCESSFULLY",
        detected_version: ipVersion,
        original_input: ip,
        anonymized_output: anonymizedIp,
        pipeline_integrity: {
            compliance_rule: "GDPR_ZERO_OCTET_MASK",
            latency_ms: Number(elapsedMs.toFixed(3))
        },
        timestamp: new Date().toISOString()
    });
});

/** Expands a possibly-compressed IPv6 address ("::1", "2001:db8::1") into its
 * full 8 hextet-group form, so downstream masking always works on real data. */
function expandIPv6(address) {
    if (!/^[0-9a-fA-F:]+$/.test(address)) throw new Error('unexpected characters in address');

    const parts = address.split('::');
    if (parts.length > 2) throw new Error('address cannot contain more than one "::"');

    let head = parts[0] ? parts[0].split(':') : [];
    let tail = parts.length === 2 && parts[1] ? parts[1].split(':') : [];

    if (parts.length === 1) {
        // No "::" compression present — must already have exactly 8 groups.
        head = address.split(':');
        if (head.length !== 8) throw new Error('expected 8 groups without "::" compression');
        return head.map(g => g.padStart(4, '0'));
    }

    const missing = 8 - (head.length + tail.length);
    if (missing < 0) throw new Error('too many groups for a compressed address');
    const middle = new Array(missing).fill('0000');

    return [...head, ...middle, ...tail].map(g => g.padStart(4, '0'));
}

module.exports = router;
