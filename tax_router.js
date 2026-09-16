/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 30 : TAX-ROUTER CORE ENGINE (CROSS-BORDER CUSTOMS BALANCER)
 * 💰 MATHEMATICAL SIMULATOR FOR DYNAMIC TAX CALCULATIONS WITHOUT DATABASE OVERHEAD
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : SIMULATION TARIFAIRE FISCALE MULTI-ZONE
 */
router.post('/', (req, res) => {
    const { base_price, destination_iso, item_category } = req.body;

    if (base_price === undefined || !destination_iso) {
        return res.status(400).json({ error: "Missing required 'base_price' or 'destination_iso' code parameters." });
    }

    const isoCode = destination_iso.toUpperCase().trim();
    console.log(`[💰 TAX-ROUTER] Execution de la matrice fiscale pour la destination: ${isoCode}`);

    // Logique stateless de soute douaniere
    let taxRate = 0.20; // Fallback Europe standard standardise
    let customsDuty = 0.0;

    if (isoCode === 'US') {
        taxRate = 0.08; // State tax simulation moyenne
        customsDuty = base_price > 800 ? 0.03 : 0.0; // Section 321 De Minimis Rule US Compliance
    } else if (isoCode === 'CA') {
        taxRate = 0.12;
        customsDuty = 0.05;
    } else if (['FR', 'DE', 'IT', 'ES'].includes(isoCode)) {
        taxRate = 0.21;
        customsDuty = base_price > 150 ? 0.04 : 0.0; // IOSS Limit validation Core Rule
    }

    const calculatedTax = Number((base_price * taxRate).toFixed(2));
    const calculatedDuty = Number((base_price * customsDuty).toFixed(2));
    const finalTotal = Number((Number(base_price) + calculatedTax + calculatedDuty).toFixed(2));

    res.status(200).json({
        status: "TAX_ROUTING_COMPUTED",
        pricing_matrix: {
            base_amount: Number(base_price),
            applied_vat_rate: `${(taxRate * 100).toFixed(0)}%`,
            tax_subtotal: calculatedTax,
            customs_duty_subtotal: calculatedDuty,
            total_invoice_load: finalTotal
        },
        compliance_check: {
            ioss_compliant: base_price <= 150,
            us_de_minimis_clearance: isoCode === 'US' && base_price <= 800
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;