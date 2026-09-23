/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 36 : CRYPTO-ADDRESS-VERIFY CORE ENGINE (WEB3 STRUCTURE AUDIT)
 * 🪙 MULTI-CHAIN ADDRESS VERIFIER — FULL CRYPTOGRAPHIC CHECKSUM COVERAGE
 *    BTC/LTC/DOGE/TRX/XRP: Base58Check (SHA-256d, per-chain version byte check)
 *    LTC/BTC/ADA: Bech32 (BIP-173) — BCH: CashAddr (dedicated polymod)
 *    ETH + EVM-compatible chains (BSC, Polygon, Avalanche, Arbitrum, Optimism,
 *    Base, Fantom...): EIP-55 (Keccak-256) — SOL: Ed25519 on-curve decompression
 */

const express = require('express');
const crypto = require('crypto');
const { keccak256 } = require('js-sha3');
const { ed25519 } = require('@noble/curves/ed25519.js');
const router = express.Router();

const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const RIPPLE_ALPHABET = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz';
const BECH32_CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l';

/** Decodes a Base58 string (with a given alphabet) into its raw byte representation. */
function base58Decode(str, alphabet = BASE58_ALPHABET) {
    let num = 0n;
    for (const char of str) {
        const idx = alphabet.indexOf(char);
        if (idx === -1) throw new Error('Invalid base58 character');
        num = num * 58n + BigInt(idx);
    }

    let hex = num.toString(16);
    if (hex.length % 2 === 1) hex = '0' + hex;
    const bytes = hex === '00' ? Buffer.alloc(0) : Buffer.from(hex, 'hex');

    // Leading zero-index characters encode leading zero bytes.
    let leadingZeros = 0;
    for (const char of str) {
        if (char === alphabet[0]) leadingZeros++;
        else break;
    }

    return Buffer.concat([Buffer.alloc(leadingZeros, 0), bytes]);
}

/**
 * Real Base58Check verification: validates the double-SHA256 checksum and, when
 * expectedVersions is supplied, cross-checks the decoded version byte against the
 * claimed chain — this rejects a checksum-valid address from one chain (e.g. BTC)
 * mistakenly or maliciously submitted under a different chain label (e.g. LTC).
 */
function verifyBase58Check(address, { alphabet = BASE58_ALPHABET, expectedVersions = null, expectedPayloadLength = null } = {}) {
    try {
        const decoded = base58Decode(address, alphabet);
        if (decoded.length < 5) return { valid: false };
        const payload = decoded.slice(0, -4);
        const checksum = decoded.slice(-4);
        const hash1 = crypto.createHash('sha256').update(payload).digest();
        const hash2 = crypto.createHash('sha256').update(hash1).digest();
        const checksumValid = hash2.slice(0, 4).equals(checksum);
        if (!checksumValid) return { valid: false, versionByte: payload[0] };
        if (expectedPayloadLength !== null && payload.length !== expectedPayloadLength) {
            return { valid: false, versionByte: payload[0], lengthMismatch: true };
        }
        if (expectedVersions && !expectedVersions.includes(payload[0])) {
            return { valid: false, versionByte: payload[0], versionMismatch: true };
        }
        return { valid: true, versionByte: payload[0] };
    } catch (e) {
        return { valid: false };
    }
}

function bech32Polymod(values) {
    const GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3];
    let chk = 1;
    for (const v of values) {
        const b = chk >> 25;
        chk = ((chk & 0x1ffffff) << 5) ^ v;
        for (let i = 0; i < 5; i++) {
            if ((b >> i) & 1) chk ^= GEN[i];
        }
    }
    return chk;
}

function bech32HrpExpand(hrp) {
    const ret = [];
    for (let i = 0; i < hrp.length; i++) ret.push(hrp.charCodeAt(i) >> 5);
    ret.push(0);
    for (let i = 0; i < hrp.length; i++) ret.push(hrp.charCodeAt(i) & 31);
    return ret;
}

/**
 * Real Bech32 checksum verification (BIP-173). Used verbatim by native SegWit
 * addresses (bc1.../ltc1...) and, with a relaxed maxLength, by Cardano's longer
 * Shelley addresses (addr1...) which reuse the same BIP-173 polymod construction.
 * expectedHrp cross-checks the human-readable prefix against the claimed chain,
 * catching e.g. a valid ltc1... Bech32 string mislabeled as a BTC address.
 */
function verifyBech32(address, { expectedHrp = null, maxLength = 90 } = {}) {
    if (address !== address.toLowerCase() && address !== address.toUpperCase()) return false; // mixed case is invalid
    const lower = address.toLowerCase();
    const pos = lower.lastIndexOf('1');
    if (pos < 1 || pos + 7 > lower.length || lower.length > maxLength) return false;

    const hrp = lower.slice(0, pos);
    if (expectedHrp && hrp !== expectedHrp) return false;

    const dataPart = lower.slice(pos + 1);
    const data = [];
    for (const char of dataPart) {
        const idx = BECH32_CHARSET.indexOf(char);
        if (idx === -1) return false;
        data.push(idx);
    }

    const values = bech32HrpExpand(hrp).concat(data);
    return bech32Polymod(values) === 1;
}

/**
 * CashAddr checksum verification (Bitcoin Cash), a distinct construction from BIP-173
 * Bech32: same base32 charset, but its own 40-bit polymod generator/target and prefix
 * expansion. The chain prefix (e.g. "bitcoincash:") is optional and defaults to
 * "bitcoincash" when omitted, per the CashAddr specification.
 */
function cashaddrPolymod(values) {
    const GEN = [0x98f2bc8e61n, 0x79b76d99e2n, 0xf33e5fb3c4n, 0xae2eabe2a8n, 0x1e4f43e470n];
    let chk = 1n;
    for (const v of values) {
        const top = chk >> 35n;
        chk = ((chk & 0x07ffffffffn) << 5n) ^ BigInt(v);
        for (let i = 0; i < 5; i++) {
            if ((top >> BigInt(i)) & 1n) chk ^= GEN[i];
        }
    }
    return chk ^ 1n;
}

function cashaddrPrefixExpand(prefix) {
    const ret = [];
    for (const char of prefix) ret.push(char.charCodeAt(0) & 0x1f);
    ret.push(0);
    return ret;
}

function verifyCashAddr(address) {
    let payload = address;
    let prefix = 'bitcoincash';
    if (payload.includes(':')) {
        const parts = payload.split(':');
        prefix = parts[0].toLowerCase();
        payload = parts[1];
    }
    if (!payload || (payload !== payload.toLowerCase() && payload !== payload.toUpperCase())) return false;
    payload = payload.toLowerCase();

    const data = [];
    for (const char of payload) {
        const idx = BECH32_CHARSET.indexOf(char);
        if (idx === -1) return false;
        data.push(idx);
    }
    if (data.length < 8) return false;

    const values = cashaddrPrefixExpand(prefix).concat(data);
    return cashaddrPolymod(values) === 0n;
}

/**
 * Real EIP-55 mixed-case checksum verification (Ethereum), using Keccak-256 of the
 * lowercase hex address to determine expected letter casing per nibble.
 */
function verifyEip55Checksum(address) {
    const stripped = address.slice(2);
    const hash = keccak256(stripped.toLowerCase());
    for (let i = 0; i < stripped.length; i++) {
        const char = stripped[i];
        if (!/[a-fA-F]/.test(char)) continue; // digits carry no casing information
        const nibble = parseInt(hash[i], 16);
        const shouldBeUpper = nibble >= 8;
        if (shouldBeUpper && char !== char.toUpperCase()) return false;
        if (!shouldBeUpper && char !== char.toLowerCase()) return false;
    }
    return true;
}

/**
 * Real Ed25519 on-curve verification (Solana public keys): decodes the Base58 payload
 * and confirms the 32-byte value decompresses to a valid point on the Edwards curve.
 */
function verifySolanaOnCurve(address) {
    try {
        const decoded = base58Decode(address);
        if (decoded.length !== 32) return false;
        ed25519.Point.fromBytes(decoded);
        return true;
    } catch (e) {
        return false;
    }
}

/** Builds the "possible cross-chain confusion" diagnostic when a checksum is valid but the version byte doesn't match the claimed chain. */
function versionMismatchDiagnostic(result, chainLabel) {
    if (result.valid) return null;
    if (result.versionMismatch) {
        return `Checksum is cryptographically valid, but the decoded version byte does not correspond to ${chainLabel}: this looks like an address from a different chain submitted under the wrong network label.`;
    }
    if (result.lengthMismatch) {
        return `Decoded payload length does not match the expected ${chainLabel} address structure.`;
    }
    return null;
}

/**
 * Validates a Bitcoin address: real cryptographic checksum verification for both
 * legacy Base58Check (1.../3...) and native SegWit Bech32 (bc1...) formats, plus
 * version-byte cross-validation to reject a checksum-valid non-BTC address
 * mislabeled as Bitcoin.
 */
function verifyBtcAddress(address) {
    if (/^bc1[a-z0-9]{6,87}$/i.test(address)) {
        return { valid: verifyBech32(address, { expectedHrp: 'bc' }), method: 'bech32_checksum' };
    }
    if (/^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/.test(address)) {
        const result = verifyBase58Check(address, { expectedVersions: [0x00, 0x05], expectedPayloadLength: 21 });
        return { valid: result.valid, method: 'base58check_checksum', diagnostic: versionMismatchDiagnostic(result, 'Bitcoin') };
    }
    return { valid: false, method: 'format_rejected' };
}

/** Validates a Litecoin address: modern Base58Check (L.../M...) or native SegWit Bech32 (ltc1...). */
function verifyLtcAddress(address) {
    if (/^ltc1[a-z0-9]{6,87}$/i.test(address)) {
        return { valid: verifyBech32(address, { expectedHrp: 'ltc' }), method: 'bech32_checksum' };
    }
    if (/^[LM][a-km-zA-HJ-NP-Z1-9]{25,34}$/.test(address)) {
        const result = verifyBase58Check(address, { expectedVersions: [0x30, 0x32], expectedPayloadLength: 21 });
        return { valid: result.valid, method: 'base58check_checksum', diagnostic: versionMismatchDiagnostic(result, 'Litecoin') };
    }
    return { valid: false, method: 'format_rejected' };
}

/** Validates a Dogecoin address: Base58Check with the Dogecoin P2PKH/P2SH version bytes. */
function verifyDogeAddress(address) {
    if (/^[DA9][a-km-zA-HJ-NP-Z1-9]{25,34}$/.test(address)) {
        const result = verifyBase58Check(address, { expectedVersions: [0x1e, 0x16], expectedPayloadLength: 21 });
        return { valid: result.valid, method: 'base58check_checksum', diagnostic: versionMismatchDiagnostic(result, 'Dogecoin') };
    }
    return { valid: false, method: 'format_rejected' };
}

/** Validates a Tron address: Base58Check with the Tron-specific 0x41 version byte. */
function verifyTrxAddress(address) {
    if (/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(address)) {
        const result = verifyBase58Check(address, { expectedVersions: [0x41], expectedPayloadLength: 21 });
        return { valid: result.valid, method: 'base58check_checksum', diagnostic: versionMismatchDiagnostic(result, 'Tron') };
    }
    return { valid: false, method: 'format_rejected' };
}

/** Validates an XRP Ledger classic address: Base58Check using Ripple's own alphabet permutation. */
function verifyXrpAddress(address) {
    if (/^r[1-9A-HJ-NP-Za-km-z]{24,34}$/.test(address)) {
        const result = verifyBase58Check(address, { alphabet: RIPPLE_ALPHABET, expectedVersions: [0x00], expectedPayloadLength: 21 });
        return { valid: result.valid, method: 'base58check_checksum_ripple_alphabet', diagnostic: versionMismatchDiagnostic(result, 'XRP Ledger') };
    }
    return { valid: false, method: 'format_rejected' };
}

/** Validates a Bitcoin Cash address: CashAddr format with its dedicated polymod checksum. */
function verifyBchAddress(address) {
    if (/^(bitcoincash:)?[qp][a-z0-9]{37,80}$/i.test(address)) {
        return { valid: verifyCashAddr(address), method: 'cashaddr_checksum' };
    }
    return { valid: false, method: 'format_rejected' };
}

/** Validates a Cardano Shelley address: genuine Bech32 (BIP-173 construction) with the "addr" HRP and a relaxed length cap (Cardano addresses can exceed Bitcoin's 90-char Bech32 limit). */
function verifyAdaAddress(address) {
    if (/^addr1[a-z0-9]{20,120}$/i.test(address)) {
        return { valid: verifyBech32(address, { expectedHrp: 'addr', maxLength: 130 }), method: 'bech32_checksum' };
    }
    return { valid: false, method: 'format_rejected' };
}

/** EVM-compatible chains (ETH, BSC, Polygon, Avalanche, Arbitrum, Optimism, Base, Fantom...) all share the same 20-byte hex address format and EIP-55 checksum construction. */
const EVM_CHAINS = new Set(['eth', 'bsc', 'bnb', 'matic', 'polygon', 'avax', 'avalanche', 'arb', 'arbitrum', 'op', 'optimism', 'base', 'ftm', 'fantom', 'celo', 'cro', 'cronos']);

function verifyEvmAddress(address) {
    const formatValid = /^0x[a-fA-F0-9]{40}$/.test(address);
    const isMixedCase = formatValid && /[a-f]/.test(address.slice(2)) && /[A-F]/.test(address.slice(2));

    if (!formatValid) {
        return { valid: false, method: 'format_rejected' };
    }
    if (isMixedCase) {
        // Real EIP-55 mixed-case checksum verification via Keccak-256.
        const valid = verifyEip55Checksum(address);
        return {
            valid,
            method: 'eip55_checksum',
            diagnostic: valid
                ? "Mixed-case address casing matches the cryptographic EIP-55 checksum."
                : "Mixed-case address casing does NOT match the expected EIP-55 checksum: likely a typo or corrupted address."
        };
    }
    // All-lowercase or all-uppercase addresses are valid unchecksummed EIP-55 forms.
    return {
        valid: true,
        method: 'format_only_unchecksummed',
        diagnostic: "Address format is valid but not checksummed (all lower/upper case): casing integrity was not verifiable."
    };
}

router.post('/', (req, res) => {
    const { address, network } = req.body;

    if (!address || !network) {
        return res.status(400).json({ error: "Missing required variables: 'address' or 'network' identifier strings." });
    }

    const targetAddress = address.trim();
    const chainType = network.toLowerCase().trim();

    console.log(`[🪙 CRYPTO-VERIFY] Analyse de soute pour l'adresse ${chainType} : ${targetAddress}`);

    let isValid = false;
    let method = 'format_only';
    let diagnostic = null;

    if (EVM_CHAINS.has(chainType)) {
        const result = verifyEvmAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'btc') {
        const result = verifyBtcAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'ltc') {
        const result = verifyLtcAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'doge') {
        const result = verifyDogeAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'trx' || chainType === 'tron') {
        const result = verifyTrxAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'xrp' || chainType === 'ripple') {
        const result = verifyXrpAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'bch') {
        const result = verifyBchAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'ada' || chainType === 'cardano') {
        const result = verifyAdaAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
        diagnostic = result.diagnostic;
    } else if (chainType === 'sol') {
        // Solana addresses are Base58-encoded Ed25519 public keys with no embedded checksum;
        // validity is instead confirmed via real on-curve Ed25519 point decompression.
        const formatValid = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(targetAddress);
        if (!formatValid) {
            isValid = false;
            method = 'format_rejected';
        } else {
            isValid = verifySolanaOnCurve(targetAddress);
            method = 'ed25519_oncurve_checksum';
            diagnostic = isValid
                ? "Base58 payload decodes to a valid 32-byte Ed25519 curve point."
                : "Base58 payload does NOT decode to a valid Ed25519 curve point: address is structurally invalid despite matching format.";
        }
    } else {
        method = 'unsupported_chain';
        diagnostic = `Chain identifier "${chainType}" is not among the supported networks (btc, ltc, doge, trx, xrp, bch, ada, sol, eth + EVM-compatible chains).`;
    }

    if (!isValid) {
        return res.status(200).json({
            status: "INVALID_CRYPTO_SYNTAX",
            valid: false,
            chain: chainType,
            address: targetAddress,
            verification_method: method,
            diagnostic: diagnostic || "Checksum mapping or network pattern format signature is non-compliant."
        });
    }

    res.status(200).json({
        status: "CRYPTO_ADDRESS_VERIFIED",
        valid: true,
        chain: chainType,
        address: targetAddress,
        verification_method: method,
        diagnostic,
        security_check: {
            payout_authorization: "GRANTED",
            structural_integrity: "STERILE"
        },
        timestamp: new Date().toISOString()
    });
});

module.exports = router;
