// main.ts — original entrypoint for make.fun's news-image-20261124 bounty.
//
// Ships the day's front page image: entry.png is drawn by a separate
// generator and copied verbatim to the output directory the gate reads.
// Before the copy the file is validated against the gate's limits — PNG
// magic only, at most 1 MiB, at most 1024x1024 pixels — and any violation
// exits 1 with a clear line on stderr. Node 22, standard library only
// (node:fs, node:path); no network, no clock, no RNG, so every run
// produces identical bytes.

import { closeSync, copyFileSync, mkdirSync, openSync, readSync, statSync } from "node:fs";
import { join } from "node:path";

/** Destination directory: MAKEFUN_OUTPUT_DIR wins, /output is the default. */
const OUTPUT_DIR: string = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

/** Name the shipped image keeps in the output directory. */
const DEST_NAME = "entry.png";

/** Source image, resolved next to this script so any cwd works. */
const SOURCE = new URL("./entry.png", import.meta.url);

/** Gate limit: the shipped file may not exceed 1 MiB. */
const MAX_FILE_BYTES = 1_048_576;

/** Gate limit: neither side of the image may exceed 1024 px. */
const MAX_DIMENSION = 1024;

/** Bytes that hold the signature plus IHDR width/height: 8 + 4 + 4 + 4 + 4. */
const HEADER_BYTES = 24;

/** The PNG signature: 89 50 4E 47 0D 0A 1A 0A. */
const PNG_MAGIC: readonly number[] = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

/** Formats the gate rejects, kept so the error can name what was found. */
const REJECTED_FORMATS: ReadonlyArray<{ name: string; bytes: readonly number[] }> = [
  { name: "JPEG", bytes: [0xff, 0xd8, 0xff] },
  { name: "GIF", bytes: [0x47, 0x49, 0x46] },
  { name: "BMP", bytes: [0x42, 0x4d] },
  { name: "RIFF (WebP/WAV/AVI)", bytes: [0x52, 0x49, 0x46, 0x46] },
];

/** Stop with exit 1 and one clear line on stderr. */
function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

/** Human-readable text for an unknown error value. */
function describe(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

/** errno code of a filesystem error, e.g. "EACCES". */
function errnoOf(err: unknown): string {
  const code = (err as { code?: unknown } | null)?.code;
  return typeof code === "string" ? code : "";
}

/** Create the output directory, failing loudly when it cannot be written to. */
function ensureOutputDir(dir: string): void {
  try {
    mkdirSync(dir, { recursive: true });
  } catch (err) {
    const code = errnoOf(err);
    if (code === "EACCES" || code === "EPERM" || code === "EROFS") {
      fail(`output directory is not writable: ${dir} (${code})`);
    }
    fail(`cannot create output directory ${dir}: ${describe(err)}`);
  }
}

/** Copy the image to its destination, mapping permission errors to a clear line. */
function writeImage(source: URL, dest: string): void {
  try {
    copyFileSync(source, dest);
  } catch (err) {
    const code = errnoOf(err);
    if (code === "EACCES" || code === "EPERM" || code === "EROFS") {
      fail(`output directory is not writable: ${dest} (${code})`);
    }
    fail(`cannot write ${dest}: ${describe(err)}`);
  }
}

/** Run a filesystem step; on failure exit 1 naming the step. */
function orDie<T>(step: string, run: () => T): T {
  try {
    return run();
  } catch (err) {
    fail(`${step}: ${describe(err)}`);
  }
}

/** Read the first `count` bytes of the source (a short read yields a short buffer). */
function readHead(count: number): Buffer {
  const fd = openSync(SOURCE, "r");
  try {
    const head = Buffer.alloc(count);
    const read = readSync(fd, head, 0, count, 0);
    return head.subarray(0, read);
  } finally {
    closeSync(fd);
  }
}

/** Render bytes as spaced hex, e.g. "ff d8 ff". */
function hex(bytes: Buffer, at: number, length: number): string {
  return Array.from(bytes.subarray(at, at + length), (b) => b.toString(16).padStart(2, "0")).join(" ");
}

/** True when `bytes` matches the start of `head`, byte by byte. */
function startsWith(head: Buffer, bytes: readonly number[]): boolean {
  if (head.length < bytes.length) return false;
  for (let i = 0; i < bytes.length; i += 1) {
    if (head[i] !== bytes[i]) return false;
  }
  return true;
}

/** Name the format the file actually is, when it is one we can recognise. */
function detectFormat(head: Buffer): string {
  for (const format of REJECTED_FORMATS) {
    if (startsWith(head, format.bytes)) return format.name;
  }
  return "unknown format";
}

/** Enforce the gate's limits on the header bytes and the file size. */
function validate(head: Buffer, size: number): void {
  if (head.length < HEADER_BYTES) {
    fail(`truncated: ${head.length} bytes cannot hold a PNG header (${HEADER_BYTES} needed)`);
  }
  if (!startsWith(head, PNG_MAGIC)) {
    const found = detectFormat(head);
    if (found === "unknown format") {
      fail(`not a PNG: magic is ${hex(head, 0, 8)}`);
    }
    fail(`unsupported ${found}: the gate accepts PNG only (magic ${hex(head, 0, 8)})`);
  }
  if (size > MAX_FILE_BYTES) {
    fail(`file is ${size} bytes; the gate allows at most ${MAX_FILE_BYTES}`);
  }
  const width = head.readUInt32BE(16);
  const height = head.readUInt32BE(20);
  if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
    fail(`image is ${width}x${height}; the gate allows at most ${MAX_DIMENSION}x${MAX_DIMENSION}`);
  }
}

function main(): void {
  const head = orDie("cannot read entry.png", () => readHead(HEADER_BYTES));
  const size = orDie("cannot stat entry.png", () => statSync(SOURCE).size);
  validate(head, size);

  const dest = join(OUTPUT_DIR, DEST_NAME);
  ensureOutputDir(OUTPUT_DIR);
  writeImage(SOURCE, dest);
  console.log(`wrote ${dest} (${size} bytes)`);
}

main();
