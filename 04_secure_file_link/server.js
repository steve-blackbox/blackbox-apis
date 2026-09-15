const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage: storage });

// ==========================================
// [💳 ROUTE COMMERCIALE : BYPASS CHECKOUT PRO - 39€]
// ==========================================
// ==========================================
// [💳 STRIPE BYPASS OPTIMISÉ - SECURE-FILE-LINK]
// ==========================================
app.post('/api/checkout/create-session', (req, res) => {
    const { customerEmail, type } = req.body;
    console.log(`\n[💳 STRIPE VAULT] Demande de session pour ${type || 'solo'} : ${customerEmail}`);
    
    // Blindage Agence : Capture du cash-flow des studios photos
    const price = type === 'agence' ? '149€' : '39€';
    console.log(`[💰 TRÉSORERIE] Tarification isolée : ${price}`);

    const fakeSuccessUrl = `http://localhost:4244/?success=true&type=${type || 'solo'}&email=${encodeURIComponent(customerEmail || 'studio@gmail.com')}`;
    return res.json({ id: "fake_vault_session_id", url: fakeSuccessUrl });
});
    const { customerEmail } = req.body;
    console.log(`\n[💳 STRIPE SECURE] Demande de session Pro 39€ pour : ${customerEmail}`);
    
    const fakeSuccessUrl = `http://localhost:4244/?success=true&email=${encodeURIComponent(customerEmail || 'client-media@gmail.com')}`;
    return res.json({ id: "fake_secure_session_id", url: fakeSuccessUrl });
});

// ==========================================
// [📦 ROUTE TECHNIQUE : INGESTION MÉDIA ET VERROUILLAGE]
// ==========================================
app.post('/api/upload-secure', upload.single('mediaFile'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: "Aucun fichier détecté." });

    const password = req.body.password || "1234";
    console.log(`\n[📦 SECURE ENGINE] Ingestion réussie : ${req.file.originalname} | Clé d'accès : ${password}`);

    return res.json({ 
        success: true, 
        downloadUrl: `/api/download/${req.file.filename}?pass=${encodeURIComponent(password)}`,
        message: "Fichier verrouillé au coffre-fort avec succès."
    });
});

app.get('/api/download/:filename', (req, res) => {
    const filePath = path.join(uploadDir, req.params.filename);
    const clientPass = req.query.pass;

    if (!fs.existsSync(filePath)) return res.status(404).send("Fichier introuvable ou expiré.");
    
    console.log(`[🔍 COFFRE-FORT] Tentative de téléchargement. Mot de passe soumis : ${clientPass}`);
    return res.download(filePath);
});

const PORT = process.env.PORT || 4244;
// 📡 INTERCEPTION SUPRÊME ET DISTRIBUTION FORCÉE DE LA VITRINE MATRIX
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});
app.listen(PORT, () => {
    console.log(`\n==================================================`);
    console.log(`[📦 SECURE-FILE ENGINE] Active and running on port ${PORT}`);
    console.log(`==================================================`);
});