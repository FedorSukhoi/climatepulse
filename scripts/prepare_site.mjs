import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Sites limits individual assets to 25 MiB. Keep workers local, but load the
// exact installed DuckDB engine version from its published npm CDN assets.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'dist');
const { version } = JSON.parse(fs.readFileSync(path.join(root, 'dashboard/node_modules/@duckdb/duckdb-wasm/package.json'), 'utf8'));
fs.rmSync(output, { recursive: true, force: true });
fs.cpSync(path.join(root, 'dashboard/build'), output, { recursive: true });
const assets = path.join(output, '_app/immutable/assets');
const chunks = path.join(output, '_app/immutable/chunks');
for (const engine of ['eh', 'mvp']) {
  const names = fs.readdirSync(assets).filter(name => name.startsWith(`duckdb-${engine}.`) && name.endsWith('.wasm'));
  if (names.length !== 1) throw new Error(`Expected one ${engine} engine, found ${names.length}`);
  const localUrl = `/_app/immutable/assets/${names[0]}`;
  const cdnUrl = `https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@${version}/dist/duckdb-${engine}.wasm`;
  let references = 0;
  for (const name of fs.readdirSync(chunks).filter(name => name.endsWith('.js'))) {
    const file = path.join(chunks, name);
    const source = fs.readFileSync(file, 'utf8');
    if (!source.includes(localUrl)) continue;
    fs.writeFileSync(file, source.replaceAll(localUrl, cdnUrl));
    references++;
  }
  if (references !== 1) throw new Error(`Expected one ${engine} loader, found ${references}`);
  fs.unlinkSync(path.join(assets, names[0]));
}
function validate(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) validate(file);
    else if (fs.statSync(file).size > 25 * 1024 * 1024) throw new Error(`Asset exceeds hosting limit: ${file}`);
  }
}
validate(output);
console.log(`Prepared Sites assets with DuckDB ${version} engines on jsDelivr.`);
