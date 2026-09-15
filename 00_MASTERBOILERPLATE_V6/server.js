const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Configuration des middlewares essentiels
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Distribution des fichiers statiques de ta vitrine Matrix
app.use(express.static(path.join(__dirname, 'public')));

// 📡 INTERCEPTION SUPRÊME ET DISTRIBUTION DE LA VITRINE MATRIX UNIQUE
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 🛍️ ROUTE STRIPE CHECKOUT ROUTER PRE-CONFIGURÉE
app.post('/v1/checkout', async (req, res) => {
    const { plan, endpoint_target } = req.body;
    console.log(`[🛍️ STRIPE INGESTION] Request caught for Plan: ${plan} | Target: ${endpoint_target}`);
    
    try {
        res.json({ url: null, error: "Stripe Real-Time Ingress: Clés secrètes en attente d'injection." });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Allumage du réacteur sur le port réseau
app.listen(PORT, () => {
    console.log(`[🚀 SERVER RUNNING] BlackBox Labs Control Active on node port: ${PORT}`);
});