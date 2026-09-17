const express = require('express');
const cors = require('cors');
const path = require('path');
const stripe = require('stripe')('sk_live_51UGJyAAQxUv6pdHqLgOfuon9e2e60SbyVvC9rT9V97H7Uf2Lp2D7x6m8B9e'); // Clé Stripe Live active

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.resolve(__dirname, 'public')));

// 🛡️ MIDDLEWARE ANTI-BOTS ET TRAFIC PARASITE
app.use((req, res, next) => {
    const userAgent = req.headers['user-agent'] || '';
    if (userAgent.includes('HeadlessChrome') || userAgent.includes('python-requests')) {
        return res.status(403).json({ error: "BlackBox Ingress: Malicious Bot Traffic Extinguished." });
    }
    next();
});

// 💳 API ENDPOINT: SECURED CHECKOUT REDIRECTION ROUTER
app.post('/v1/checkout', async (req, res) => {
    const { planType } = req.body;
    
    // 🟢 BLINDAGE DE SÔUTE ABSOLU (Anti-Friction Casse & Secours Client)
    const cleanPlan = String(planType || '').toLowerCase().trim();
    let targetPriceId = '';

    if (cleanPlan === 'core') {
        targetPriceId = 'price_1UGZfMAQxUv6pdHqGs0lj7wW'; // 49\$ BlackBox AI - Core Matrix (NEUF)
    } else {
        // Sécurité maximale : si cache 'labs', 'agency' ou vide, on force le plan Premium à 149\(targetPriceId = 'price_1UGZgCAQxUv6pdHqIqMShwHM'; // 149\) BlackBox AI - labs All-Access (NEUF)
    }

    try {
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [{ price: targetPriceId, quantity: 1 }],
            mode: 'payment',
            success_url: `${req.headers.origin || 'https://blackbox-apis.com'}?session=success`,
            cancel_url: `${req.headers.origin || 'https://blackbox-apis.com'}?session=cancel`,
        });
        res.json({ url: session.url });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/', (req, res) => {
    res.sendFile(path.resolve(__dirname, 'public', 'index.html'));
});

app.get('*', (req, res) => {
    res.redirect('/');
});

app.listen(PORT, () => console.log(`🚀 BlackBox Stream fully armed on port ${PORT}`));