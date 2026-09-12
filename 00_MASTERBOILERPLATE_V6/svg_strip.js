/**
 * Robot 09: SVG-STRIP (Version Cloud-Native Core)
 * Optimisation, minification et épuration de structures XML/SVG
 * Poids cible : < 1.5KB
 */
function cleanAndMinifySVG(rawSVG) {
    if (!rawSVG || typeof rawSVG !== 'string') return '';

    let cleaned = rawSVG;

    // 1. Suppression des commentaires XML/HTML
    cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '');

    // 2. Suppression de la déclaration XML et Doctype
    cleaned = cleaned.replace(/<\?xml[\s\S]*?\?>/i, '');
    cleaned = cleaned.replace(/<!DOCTYPE[\s\S]*?>/i, '');

    // 3. Suppression des métadonnées Figma, Illustrator, Inkscape
    cleaned = cleaned.replace(/<(metadata|defs|sodipodi:namedview|inkscape:grid)[\s\S]*?<\/\1>/gi, '');
    cleaned = cleaned.replace(/<(metadata|defs|sodipodi:namedview|inkscape:grid)[^>]*?\/>/gi, '');

    // 4. Purge des attributs parasites des éditeurs graphiques
    cleaned = cleaned.replace(/\s(inkscape|sodipodi|i|x):[a-z0-9-]+="[^"]*"/gi, '');
    cleaned = cleaned.replace(/\sxml:space="[^"]*"/gi, '');
    cleaned = cleaned.replace(/\sid="Svgjs[A-Za-z0-9]+"/gi, '');

    // 5. Minification agressive des blancs
    cleaned = cleaned.replace(/\s+/g, ' ');
    cleaned = cleaned.replace(/>\s+</g, '><');
    cleaned = cleaned.replace(/\s*([=\/>])\s*/g, '$1');

    return cleaned.trim();
}

module.exports = { cleanAndMinifySVG };