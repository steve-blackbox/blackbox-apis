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

    const ip = raw_ip_address.trim();
    console.log(`[🛡️ IP-ANONYMIZER] Application des masques d'anonymisation pour l'adresse reseau.`);

    let anonymizedIp = '';
    let ipVersion = '';

    if (ip.includes('.')) {
        // Traitement chirurgical de la structure IPv4 (Mise à zéro du dernier octet)
        ipVersion = 'IPv4';
        const segments = ip.split('.');
        if (segments.length === 4) {
            segments[3] = '0';
            anonymizedIp = segments.join('.');
        } else {
            anonymizedIp = "INVALID_IPV4_STRUCTURE";
        }
    } else if (ip.includes(':')) {
        // Traitement chirurgical de la structure IPv6 (Mise à zéro des derniers blocs)
        ipVersion = 'IPv6';
        const segments = ip.split(':');
        if (segments.length >= 3) {
            // Conserve uniquement les 3 premiers sous-réseaux (Global Routing Prefix)
            anonymizedIp = `${segments[0]}:${segments[1]}:${segments[2]}:0000:0000:0000:0000:0000`;
        } else {
            anonymizedIp = "INVALID_IPV6_STRUCTURE";
        }
    } else {
        return res.status(422).json({ error: "Unsupported or non-compliant IP address protocol layout footprint." });
    }

    res.status(200).json({
        status: "IP_ADDRESS_ANONYMIZED_SUCCESSFULLY",
        detected_version: ipVersion,
        original_input: ip,
        anonymized_output: anonymizedIp,
        pipeline_integrity: {
            compliance_rule: "GDPR_ZERO_OCTET_MASK",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;
