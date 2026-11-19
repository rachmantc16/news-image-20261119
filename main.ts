// news-image-20261119: validate the entry image and copy it to the output dir.
// Node 22, standard library only. Usage:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1048576; // 1 MiB
const MAX_SIDE = 1024;

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

let bytes: Buffer;
try {
  bytes = readFileSync(source);
} catch {
  fail(`cannot read ${source}`);
}

if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}

// PNG signature: 89 50 4E 47 0D 0A 1A 0A
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_SIG)) {
  fail('entry.png is not a PNG file (bad signature)');
}

// First chunk must be IHDR; width and height are big-endian uint32 at offsets 16 and 20.
if (bytes.toString('latin1', 12, 16) !== 'IHDR') {
  fail('entry.png has no IHDR chunk');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width === 0 || height === 0 || width > MAX_SIDE || height > MAX_SIDE) {
  fail(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}

// A well-formed PNG ends with a 12-byte IEND chunk.
if (bytes.length < 45 || bytes.toString('latin1', bytes.length - 8, bytes.length - 4) !== 'IEND') {
  fail('entry.png is truncated (no IEND chunk)');
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);
const copied = statSync(target).size;
if (copied !== bytes.length) {
  fail(`copied file is ${copied} bytes, expected ${bytes.length}`);
}
console.log(`wrote ${target} (${width}x${height}, ${bytes.length} bytes)`);
