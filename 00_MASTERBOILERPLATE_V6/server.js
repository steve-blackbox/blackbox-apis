const express = require('express');
const path = require('path');
// 🚀 INJECTION EN DUR : Force le passage outre la variable d'environnement pour percer le pop-up
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/v1/checkout', async (req, res) => {
    const { plan, endpoint_target } = req.body;
    console.log(`[🛍️ STRIPE FORCE] Mode Bypass activé pour Plan: ${plan}`);
    
    let amount = plan === 'agency' ? 14900 : 4900; 
    let productName = plan === 'agency' ? 'LABS ALL-ACCESS' : 'CORE ACCESS';

    try {
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [{
                price_data: {
                    currency: 'usd',
                    product_data: {
                        name: productName,
                        description: `Lifetime Access Key bound to node: ${endpoint_target}`,
                    },
                    unit_amount: amount,
                },
                quantity: 1,
            }],
            mode: 'payment',
            success_url: `${req.protocol}://${req.get('host')}/success.html`,
            cancel_url: `${req.protocol}://${req.get('host')}/cancel.html`,
        });

        res.json({ url: session.url });
    } catch (err) {
        console.error(`[🚨 CRASH INGESTION] ${err.message}`);
        // Renvoie l'erreur réelle de Stripe au lieu de l'ancien message pour voir le verdict
        res.status(500).json({ error: `Stripe Refusal: ${err.message}` });
    }
});

app.listen(PORT, () => {
    console.log(`[🚀 SERVER BYPASS LIVE] BlackBox Labs Engine opérant sur le port réseau: ${PORT}`);
});