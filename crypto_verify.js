/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT 36 : CRYPTO-ADDRESS-VERIFY CORE ENGINE (WEB3 STRUCTURE AUDIT)
 * 🪙 MULTI-CHAIN ADDRESS VERIFIER — REAL CHECKSUM VALIDATION WHERE POSSIBLE
 */

const express = require('express');
const crypto = require('crypto');
const router = express.Router();

const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const BECH32_CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l';

/** Decodes a Base58 string into its raw byte representation. */
function base58Decode(str) {
    let num = 0n;
    for (const char of str) {
        const idx = BASE58_ALPHABET.indexOf(char);
        if (idx === -1) throw new Error('Invalid base58 character');
        num = num * 58n + BigInt(idx);
    }

    let hex = num.toString(16);
    if (hex.length % 2 === 1) hex = '0' + hex;
    const bytes = hex === '00' ? Buffer.alloc(0) : Buffer.from(hex, 'hex');

    // Leading '1' characters encode leading zero bytes.
    let leadingZeros = 0;
    for (const char of str) {
        if (char === '1') leadingZeros++;
        else break;
    }

    return Buffer.concat([Buffer.alloc(leadingZeros, 0), bytes]);
}

/** Real Base58Check verification (used by legacy Bitcoin addresses starting with 1 or 3). */
function verifyBase58Check(address) {
    try {
        const decoded = base58Decode(address);
        if (decoded.length < 5) return false;
        const payload = decoded.slice(0, -4);
        const checksum = decoded.slice(-4);
        const hash1 = crypto.createHash('sha256').update(payload).digest();
        const hash2 = crypto.createHash('sha256').update(hash1).digest();
        return hash2.slice(0, 4).equals(checksum);
    } catch (e) {
        return false;
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

/** Real Bech32 checksum verification (BIP-173, used by native SegWit addresses like bc1...). */
function verifyBech32(address) {
    if (address !== address.toLowerCase() && address !== address.toUpperCase()) return false; // mixed case is invalid
    const lower = address.toLowerCase();
    const pos = lower.lastIndexOf('1');
    if (pos < 1 || pos + 7 > lower.length || lower.length > 90) return false;

    const hrp = lower.slice(0, pos);
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
 * Validates a Bitcoin address: real cryptographic checksum verification for both
 * legacy Base58Check (1.../3...) and native SegWit Bech32 (bc1...) formats.
 */
function verifyBtcAddress(address) {
    if (/^bc1[a-z0-9]{6,87}$/i.test(address)) {
        return { valid: verifyBech32(address), method: 'bech32_checksum' };
    }
    if (/^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/.test(address)) {
        return { valid: verifyBase58Check(address), method: 'base58check_checksum' };
    }
    return { valid: false, method: 'format_rejected' };
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

    if (chainType === 'eth') {
        isValid = /^0x[a-fA-F0-9]{40}$/.test(targetAddress);
        method = 'format_only';
        // Real EIP-55 mixed-case checksum verification requires Keccak-256, which is not
        // covered here. Purely lowercase/uppercase addresses are valid unchecksummed forms;
        // mixed-case addresses are accepted on format only and flagged as unverified.
        if (isValid && /[a-f]/.test(targetAddress.slice(2)) && /[A-F]/.test(targetAddress.slice(2))) {
            diagnostic = "Mixed-case address detected: EIP-55 checksum casing was NOT cryptographically verified, format only.";
        }
    } else if (chainType === 'btc') {
        const result = verifyBtcAddress(targetAddress);
        isValid = result.valid;
        method = result.method;
    } else if (chainType === 'sol') {
        // Solana addresses are Base58-encoded Ed25519 public keys with no embedded checksum;
        // real validation requires curve-point verification, out of scope here. Format only.
        isValid = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(targetAddress);
        method = 'format_only';
        if (isValid) {
            diagnostic = "Solana public key format is valid; on-curve Ed25519 verification was not performed.";
        }
    }

    if (!isValid) {
        return res.status(200).json({
            status: "INVALID_CRYPTO_SYNTAX",
            valid: false,
            chain: chainType,
            address: targetAddress,
            verification_method: method,
            diagnostic: "Checksum mapping or network pattern format signature is non-compliant."
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
