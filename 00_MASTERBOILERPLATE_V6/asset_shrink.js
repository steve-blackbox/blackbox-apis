// =========================================================================
// ROBOT 08 — ASSET-SHRINK HIGH-VELOCITY LOCAL WEBP COMPRESSOR (v1.0)
// ARCHITECTURE LAYER — 100% CLIENT-SIDE CANVAS RECONSTRUCTION LOOPS
// =========================================================================

/**
 * Compresse et convertit une image JPEG/PNG au format WebP en local pur.
 * @param {File} file - Le fichier image brut déposé par le client US.
 * @param {number} quality - Le taux de compression (de 0.1 à 1.0, défaut 0.80).
 * @returns {Promise<Object>} - L'asset ultra-léger nettoyé et compressé.
 */
function compressImageAsset(file, quality = 0.80) {
    return new Promise((resolve, reject) => {
        if (!file) return reject("🚨 ERROR: Empty file blob inside target input buffer.");
        if (!file.type.startsWith('image/')) return reject("🚨 ERROR: Target asset must be a valid image format.");

        const reader = new FileReader();
        reader.readAsDataURL(file);
        
        reader.onload = function (event) {
            const img = new Image();
            img.src = event.target.result;
            
            img.onload = function () {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Alignement des dimensions d'origine au pixel près
                canvas.width = img.width;
                canvas.height = img.height;
                
                // Redessin géométrique instantané : élimination des blocs corrompus et métadonnées
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                // Conversion et compression native au format WebP (Silicon Valley standard 2026)
                canvas.toBlob((blob) => {
                    if (!blob) return reject("🚨 ERROR: Local canvas compression loop crashed.");
                    
                    const savedBytes = file.size - blob.size;
                    const compressionRatio = ((savedBytes / file.size) * 100).toFixed(1);
                    
                    console.log(`[🏆 ASSET-SHRINK] Optimized. Size reduced by ${compressionRatio}% (${blob.size} bytes).`);
                    
                    resolve({
                        cleanBlob: blob,
                        previewUrl: URL.createObjectURL(blob),
                        fileName: file.name.replace(/\.[^/.]+$/, "") + ".webp",
                        reductionPercent: compressionRatio
                    });
                }, 'image/webp', quality);
            };
        };
        reader.onerror = (error) => reject(error);
    });
}

// Initialisation passive de l'injecteur sur la console
console.log("[⚙️ ENGINE] Robot 08 Asset-Shrink dynamic local canvas worker loaded.");