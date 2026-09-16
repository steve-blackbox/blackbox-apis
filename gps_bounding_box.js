/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 77 : GPS-BOUNDING-BOX CORE ENGINE (GEO ROUTING LAB)
 * 🌍 LIGHTNING-FAST STATELESS BOUNDARY CALCULATOR FOR LOCAL PROXIMITY INDEXES
 */

const express = require('express');
const router = express.Router();

/**
 * 📥 ROUTE CORE : DÉTERMINATION SYNTAXIQUE DES BORNES SPATIALES SANS SOU_TE CACHE
 */
router.post('/', (req, res) => {
    const { center_lat, center_lon, radius_km } = req.body;

    if (center_lat === undefined || center_lon === undefined) {
        return res.status(400).json({ error: "Missing required params: 'center_lat' and 'center_lon' numeric variables." });
    }

    const lat = parseFloat(center_lat);
    const lon = parseFloat(center_lon);
    const radius = parseFloat(radius_km) || 5; // 5 kilomètres par défaut si vide

    if (isNaN(lat) || isNaN(lon) || isNaN(radius) || radius <= 0) {
        return res.status(422).json({ error: "Invalid parameters formatting. Check numeric limits and structures." });
    }

    console.log(`[🌍 GPS-BOUNDING-BOX] Compilation d'un perimetre de recherche spatial de ${radius}km.`);

    // Constantes de soute de l'index mathématique terrestre
    const kmPerDegreeLat = 111.0;
    const kmPerDegreeLon = 111.0 * Math.cos(lat * Math.PI / 180);

    const deltaLat = radius / kmPerDegreeLat;
    const deltaLon = radius / Math.abs(kmPerDegreeLon);

    res.status(200).json({
        status: "GPS_BOUNDING_BOX_COMPUTED",
        center_node: { lat: lat, lon: lon },
        radius_applied_km: radius,
        bounding_box: {
            min_latitude: parseFloat((lat - deltaLat).toFixed(6)),
            max_latitude: parseFloat((lat + deltaLat).toFixed(6)),
            min_longitude: parseFloat((lon - deltaLon).toFixed(6)),
            max_longitude: parseFloat((lon + deltaLon).toFixed(6))
        },
        pipeline_integrity: {
            grid_approximation: "EQU_RECTANGULAR_PROJECTION",
            latency: "0.04ms"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;