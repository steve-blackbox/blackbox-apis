const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// ==========================================
// [💳 ROUTE COMMERCIALE : CHEKOUT BYPASS - LINK-SHIELD PRO]
// ==========================================
app.post('/api/checkout/create-session', (req, res) => {
    const { customerEmail, type } = req.body;
    console.log(`\n[💳 STRIPE LINK] Demande de session pour ${type || 'solo'} : ${customerEmail}`);
    
    const price = type === 'agence' ? '149€' : '49€';
    console.log(`[💰 TRÉSORERIE] Tarification détectée : ${price}`);

    const fakeSuccessUrl = `http://localhost:4245/?success=true&email=${encodeURIComponent(customerEmail || 'test-marketing@gmail.com')}`;
    return res.json({ id: "fake_link_session_id", url: fakeSuccessUrl });
});

// ==========================================
// [🔗 MOTEUR TECHNIQUE : MASQUAGE ET REDIRECTION INVISIBLE]
// ==========================================
// Simulation de base locale JSON contenant les liens d'affiliation protégés
const linksDatabase = {
    "formation-crypto": "https://formation-crypto-affilie.com",
    "outil-seo": "https://logiciel-seo-premium.com",
    "hebergement-cloud": "https://hoster-premium.com"
};

app.get('/go/:slug', (req, res) => {
    const slug = req.params.slug;
    const realDestination = linksDatabase[slug];

    if (!realDestination) {
        console.log(`[❌ LINK ENGINE] Lien introuvable ou expiré pour le slug : /go/${slug}`);
        return res.status(404).send("Lien de redirection introuvable ou expiré.");
    }

    console.log(`\n[🔗 MASQUAGE ACTIF] Redirection clinique exécutée : /go/${slug} ➔ ${realDestination}`);
    
    // Redirection stérile 302 pour bypasser les extensions pirates de navigateurs
    return res.redirect(realDestination);
});

// Ancrage étanche sur le port 4245 (Zéro collision réseau)
const PORT = process.env.PORT || 4245;
app.listen(PORT, () => {
    console.log(`\n==================================================`);
    console.log(`[🔗 LINK-SHIELD ENGINE] Active and running on port ${PORT}`);
    console.log(`==================================================`);
});