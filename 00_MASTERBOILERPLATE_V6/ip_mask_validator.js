/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 45 : IP-MASK-VALIDATOR CORE ENGINE (GEOLOCK & ROUTING LAB)
 * 🌐 STATELESS REGEX CIDR BOUNDARY INSPECTOR FOR NETWORKING SUBNETS
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : VALIDATION SYNTAXIQUE DES INFRASTRUCTURES CIDR (IPv4/IPv6)
 */
router.post('/', (req, res) => {
    const { cidr_string } = req.body;

    if (!cidr_string) {
        return res.status(400).json({ error: "Missing required 'cidr_string' parameter variable string." });
    }

    const cleanCidr = cidr_string.trim();
    console.log(`[🌐 IP-MASK-VALIDATOR] Scan de conformite reseau pour la notation : ${cleanCidr}`);

    // Regex chirurgicale IPv4 CIDR (Ex: 192.168.0.0/24)
    const ipv4CidrRegex = /^(([0-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}([0-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\/([0-9]|[1-2]\d|3[0-2])$/;
    
    // Regex de soute IPv6 CIDR basique
    const ipv6CidrRegex = /^s*([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\/([0-9]|[1-9]\d|1[0-1]\d|12[0-8])\s*$/;

    const isV4 = ipv4CidrRegex.test(cleanCidr);
    const isV6 = !isV4 && ipv6CidrRegex.test(cleanCidr);

    if (!isV4 && !isV6) {
        return res.status(200).json({
            status: "MALFORMED_CIDR_NOTATION",
            valid: false,
            input_received: cleanCidr,
            diagnostic: "The string structure or bitmask ranges are non-compliant with standard subnet naming rules."
        });
    }

    res.status(200).json({
        status: "IP_CIDR_MASK_VALIDATED",
        valid: true,
        input_received: cleanCidr,
        network_layer: isV4 ? "IPv4" : "IPv6",
        allocation: {
            routing_integrity: "STERILE_SECURE",
            subnet_mask_bit: cleanCidr.split('/')[1]
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;