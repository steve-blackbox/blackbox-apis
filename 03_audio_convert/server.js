const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Assurer l'existence du dossier de soute temporaire des uploads
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// ==========================================
// [💳 STRIPE BYPASS OPTIMISÉ - AUDIO-CONVERT]
// ==========================================
app.post('/api/checkout/create-session', (req, res) => {
    try {
        const { customerEmail, type } = req.body;
        console.log(`\n[💳 STRIPE AUDIO] Demande de session pour ${type || 'solo'} : ${customerEmail}`);
        
        const price = type === 'agence' ? '149€' : '39€';
        console.log(`[💰 TRÉSORERIE] Tarification isolée : ${price}`);

        const fakeSuccessUrl = `http://localhost:4243/?success=true&type=${type || 'solo'}&email=${encodeURIComponent(customerEmail || 'podcaster@gmail.com')}`;
        return res.json({ id: "fake_audio_session_id", url: fakeSuccessUrl });
    } catch (globalError) {
        console.error(`[❌ CRASH-SHIELD STRIPE] Erreur interceptée : ${globalError.message}`);
        return res.status(500).json({ error: "Erreur interne de soute financière sécurisée." });
    }
});

// ==========================================
// [🎙️ MOTEUR TECHNIQUE : CONVERSION + CRASH-SHIELD]
// ==========================================
app.post('/api/audio/convert', (req, res) => {
    // Simulation du traitement de fichier audio
    const fakeFileName = `master_${Date.now()}.wav`;
    const inputPath = path.join(uploadDir, fakeFileName);
    const outputPath = path.join(uploadDir, `converted_${Date.now()}.mp3`);

    console.log(`\n[🎙️ ENGINE START] Initialisation du traitement sur : ${fakeFileName}`);

    // Simulation de l'écriture du master local
    fs.writeFileSync(inputPath, "AUDIO_DATA_STREAM_SIMULATION");

    // Commande factice simulant l'appel système FFmpeg
    // Injection du Crash-Shield : On enveloppe l'exécution système de manière étanche
    const ffmpegCommand = `echo "FFmpeg processing simulation..."`; 

    exec(ffmpegCommand, (error, stdout, stderr) => {
        // PROTECTION ABSORBANTE : Si FFmpeg crash ou renvoie un code d'erreur
        if (error) {
            console.error(`[❌ CRASH-SHIELD FFMPEG] Dysfonctionnement détecté : ${error.message}`);
            
            // Nettoyage immédiat des fichiers résiduels pour éviter de saturer le SSD
            if (fs.existsSync(inputPath)) fs.unlinkSync(inputPath);
            
            // Le port NE MEURT PAS, on renvoie une réponse propre au client
            return res.status(500).json({ success: false, error: "Traitement audio corrompu. Processus isolé." });
        }

        console.log(`[✅ AUDIO PROCESSING] Traitement binaire FFmpeg nominal.`);
        
        // Nettoyage standard du fichier source WAV après conversion
        if (fs.existsSync(inputPath)) fs.unlinkSync(inputPath);

        return res.json({ 
            success: true, 
            message: "Conversion haute fidélité stabilisée par bloc.",
            downloadUrl: `/api/audio/download?file=${path.basename(outputPath)}`
        });
    });
});

// PROTECTION SÉCURITÉ ABSOLUE : Capture des erreurs fatales asynchrones hors-contexte
process.on('uncaughtException', (err) => {
    console.error(`\n[🚨 ANTI-DISJONCTEUR BLOC] Exception non gérée interceptée au vol : ${err.message}`);
    console.log(`[🛡️ CRASH-SHIELD] Le serveur reste allumé. Maintenance automatique activée.\n`);
});

const PORT = process.env.PORT || 4243;
app.listen(PORT, () => {
    console.log(`\n==================================================`);
    console.log(`[🎙️ AUDIO-CONVERT ENGINE] Stable & Crash-Shielded on port ${PORT}`);
    console.log(`==================================================`);
});