/**
 * 🛰️ BLACKBOX AUTOMATED CONTROL — APIS CONSTELLATION
 * 🤖 ROBOT : EXIF-CLOAK CORE ENGINE (IMAGE METADATA STRIPPER)
 * 🖼️ BINARY-LEVEL JPEG SEGMENT PARSER — REMOVES EXIF (APP1) & COMMENT (COM) SEGMENTS
 */

const express = require('express');
const router = express.Router();

/**
 * Strips EXIF (APP1) and comment (COM) segments from a JPEG buffer by walking
 * its marker segments directly, leaving image data and other segments (e.g. JFIF/APP0)
 * intact. Returns the cleaned buffer plus how many segments were removed.
 */
function stripJpegMetadata(buffer) {
    if (buffer.length < 4 || buffer[0] !== 0xFF || buffer[1] !== 0xD8) {
        throw new Error('Not a valid JPEG buffer (missing SOI marker 0xFFD8)');
    }

    const chunks = [buffer.slice(0, 2)]; // keep SOI marker
    let offset = 2;
    let strippedSegments = 0;

    while (offset < buffer.length - 1) {
        if (buffer[offset] !== 0xFF) break; // malformed / reached raw entropy-coded data

        const marker = buffer[offset + 1];

        // Start Of Scan: everything after this is compressed image data, copy as-is and stop.
        if (marker === 0xDA) {
            chunks.push(buffer.slice(offset));
            offset = buffer.length;
            break;
        }

        // End of image marker.
        if (marker === 0xD9) {
            chunks.push(buffer.slice(offset, offset + 2));
            offset += 2;
            continue;
        }

        // Markers with no payload length (TEM, RSTn).
        if (marker === 0x01 || (marker >= 0xD0 && marker <= 0xD7)) {
            chunks.push(buffer.slice(offset, offset + 2));
            offset += 2;
            continue;
        }

        const length = buffer.readUInt16BE(offset + 2);
        const segmentEnd = offset + 2 + length;

        // APP1 (0xFFE1) typically carries EXIF/XMP metadata, COM (0xFFFE) carries free-text comments.
        if (marker === 0xE1 || marker === 0xFE) {
            strippedSegments++;
        } else {
            chunks.push(buffer.slice(offset, segmentEnd));
        }

        offset = segmentEnd;
    }

    return { buffer: Buffer.concat(chunks), strippedSegments };
}

/**
 * Strips ancillary metadata chunks (tEXt, iTXt, zTXt, eXIf, tIME) from a PNG buffer,
 * keeping critical chunks (IHDR, PLTE, IDAT, IEND) intact.
 */
function stripPngMetadata(buffer) {
    const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);
    if (!buffer.slice(0, 8).equals(PNG_SIGNATURE)) {
        throw new Error('Not a valid PNG buffer (bad signature)');
    }

    const METADATA_TYPES = new Set(['tEXt', 'iTXt', 'zTXt', 'eXIf', 'tIME']);
    const chunks = [buffer.slice(0, 8)];
    let offset = 8;
    let strippedSegments = 0;

    while (offset < buffer.length) {
        const length = buffer.readUInt32BE(offset);
        const type = buffer.slice(offset + 4, offset + 8).toString('ascii');
        const chunkEnd = offset + 12 + length; // length + type(4) + data(length) + crc(4)

        if (METADATA_TYPES.has(type)) {
            strippedSegments++;
        } else {
            chunks.push(buffer.slice(offset, chunkEnd));
        }

        offset = chunkEnd;
        if (type === 'IEND') break;
    }

    return { buffer: Buffer.concat(chunks), strippedSegments };
}

router.post('/', (req, res) => {
    try {
        const { image_base64 } = req.body;
        if (!image_base64 || typeof image_base64 !== 'string') {
            return res.status(400).json({ error: "Missing required 'image_base64' payload string." });
        }

        let inputBuffer;
        try {
            inputBuffer = Buffer.from(image_base64, 'base64');
        } catch (e) {
            return res.status(400).json({ error: "Invalid base64 payload." });
        }

        if (inputBuffer.length < 8) {
            return res.status(400).json({ error: "Payload too small to be a valid image." });
        }

        const isJpeg = inputBuffer[0] === 0xFF && inputBuffer[1] === 0xD8;
        const isPng = inputBuffer.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]));

        let result;
        let format;

        if (isJpeg) {
            result = stripJpegMetadata(inputBuffer);
            format = 'jpeg';
        } else if (isPng) {
            result = stripPngMetadata(inputBuffer);
            format = 'png';
        } else {
            return res.status(422).json({
                status: "UNSUPPORTED_FORMAT",
                message: "Only JPEG and PNG binary structures are supported for real metadata stripping."
            });
        }

        console.log(`[🛡️ EXIF-CLOAK] ${result.strippedSegments} metadata segment(s) removed from ${format.toUpperCase()} image.`);

        res.status(200).json({
            status: "SUCCESS",
            format,
            segments_removed: result.strippedSegments,
            output_size_bytes: result.buffer.length,
            cleaned_image_base64: result.buffer.toString('base64')
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
