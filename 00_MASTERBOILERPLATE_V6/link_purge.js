// =========================================================================
// ROBOT 07 — LINK-PURGE INLINE STERILIZATION ENGINE
// ARCHITECTURE LAYER — 100% CLIENT-SIDE URL CLEANING LOOP
// =========================================================================

/**
 * Purge les paramètres de tracking d'une URL brute en local.
 * @param {string} rawUrl - L'URL polluée collée par l'utilisateur.
 * @returns {string} - L'URL stérile et nettoyée.
 */
function cleanTrackingParameters(rawUrl) {
    try {
        let urlObj = new URL(rawUrl.trim());
        
        // Liste noire des paramètres de tracking à éjecter (Silicon Valley Standard 2026)
        const trackingBlacklist = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id',
            'fbclid', 'gclid', 'dclid', 'msclkid', 'gclsrc',
            'srsltid', // Le parasite agressif de Google Shopping 2026
            'twclid', 'igshid', 'ttclid'
        ];

        // Nettoyage chirurgical des paramètres de recherche
        trackingBlacklist.forEach(param => {
            if (urlObj.searchParams.has(param)) {
                urlObj.searchParams.delete(param);
                console.log(`[🧹 PURGED] Parameter destroyed: ${param}`);
            }
        });

        // Reconstruction de l'URL stérile
        return urlObj.toString();
    } catch (error) {
        console.error("🚨 ERROR: Invalid URL payload format.");
        return rawUrl; // Renvoie l'input initial en cas d'erreur de parsing
    }
}

// Initialisation passive des injecteurs sur l'interface
console.log("[⚙️ ENGINE] Robot 07 Link-Purge dynamic worker algorithm active.");