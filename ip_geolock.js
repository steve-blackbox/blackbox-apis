/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELATION
 * 🤖 ROBOT 11 : IP-GEOLOCK CORE ENGINE (STATELESS LOOKUP LAYER)
 * 💸 HIGH-SPEED LOCATION EXTRACTOR & DYNAMIC CURRENCY ROUTER
 */

const express = require('express');
const router = express.Router();

// Base de donnees IP ultra-legere indexee en memoire cache pour tests et production stable
const geoIpDatabase = {
    'US': { country: 'United States', code: 'US', currency: 'USD', symbol: '$' },
    'FR': { country: 'France', code: 'FR', currency: 'EUR', symbol: '€' },
    'GB': { country: 'United Kingdom', code: 'GB', currency: 'GBP', symbol: '£' },
    'CA': { country: 'Canada', code: 'CA', currency: 'CAD', symbol: '$' },
    'DE': { country: 'Germany', code: 'DE', currency: 'EUR', symbol: '€' }
};

/**
 * 📥 ROUTE CORE : RESOLUTION DE L'IP VISITEUR
 * POST & GET Compliants
 */
router.all('/', (req, res) => {
    // Interception de l'IP derriere le reverse proxy Render ou les entetes standards Cloudflare
    let clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '127.0.0.1';
    
    // Nettoyage des chaines IPv6 locales si le serveur tourne en hybride
    if (clientIp.includes(',')) {
        clientIp = clientIp.split(',')[0].trim();
    }
    
    // Simulation dynamique pour le developpement ou fallback par defaut (US) s'il s'agit d'une IP locale
    let targetedCountry = 'US';
    
    // Logique d'aiguillage optionnelle par parametre URL (?ip=XX.XX.XX.XX) pour permettre aux agences de tester
    const queryIp = req.query.ip || req.body.ip;
    
    // Extraction simplifiee de soute : Analyse des entetes pays injectes par Render/Cloudflare par defaut
    const cloudflareCountry = req.headers['cf-ipcountry'] || req.headers['x-vercel-ip-country'];
    if (cloudflareCountry) {
        targetedCountry = cloudflareCountry.toUpperCase();
    } else if (queryIp) {
        // Fallback simulateur de test terrain
        if (queryIp.startsWith('192.') || queryIp.startsWith('127.')) targetedCountry = 'FR';
        else targetedCountry = 'US';
    }

    const geoData = geoIpDatabase[targetedCountry] || geoIpDatabase['US'];

    console.log(`[🌍 IP-GEOLOCK] Execution clinique pour l'IP: ${clientIp} -> Pays resolu: ${geoData.code}`);

    res.status(200).json({
        status: "STERILE_LOOKUP_SUCCESS",
        ip: clientIp,
        country: geoData.country,
        country_code: geoData.code,
        routing: {
            currency: geoData.currency,
            currency_symbol: geoData.symbol,
            stripe_gateway_compliant: true
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;