/**
 * Robot 10: JSON-FLATTEN (Version Cloud-Native Core)
 * Aplatit les objets JSON profondément imbriqués en un seul niveau de clés
 * Poids cible : < 1KB
 */
function flattenObject(obj, prefix = '', res = {}) {
    if (!obj || typeof obj !== 'object') return res;

    for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
            const propName = prefix ? `${prefix}.${key}` : key;

            if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
                flattenObject(obj[key], propName, res);
            } else {
                res[propName] = obj[key];
            }
        }
    }
    return res;
}

module.exports = { flattenObject };