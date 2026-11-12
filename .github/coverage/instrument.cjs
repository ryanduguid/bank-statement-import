// Copyright 2026 Ryan Duguid
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

'use strict';

// The Odoo asset host uses JavaScript. Istanbul supplies its original AST maps.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const { createInstrumenter, readInitialCoverage } = require('istanbul-lib-instrument');

const inventory = {
  'account-invoicing': [
    'account_tax_fixed_amount_currency/static/src/helpers/account_tax.esm.js',
    'account_tax_fixed_amount_multiplier/static/src/helpers/account_tax.esm.js',
  ],
  'bank-statement-import': [
    'account_statement_import_online_gocardless/static/src/js/select_bank_widget.esm.js',
    'account_statement_import_online_plaid/static/src/js/plaid_integration.esm.js',
    'account_statement_import_online_plaid/static/src/lib/link/v2/stable/link-initialize.js',
  ],
};
const digest = data => createHash('sha256').update(data).digest('hex');

function ownedFile(root, relative) {
  const filename = path.join(root, relative);
  assert(fs.lstatSync(filename).isFile(), 'Source must be a regular owned file');
  assert(fs.realpathSync(filename).startsWith(fs.realpathSync(root) + path.sep), 'Source escaped root');
  return filename;
}

function prepare(relative, original) {
  const source = new TextDecoder('utf-8', { fatal: true }).decode(original).replace(/\r\n/g, '\n');
  assert(!/\b(?:istanbul|c8|v8)\s+ignore\b/.test(source), 'Coverage ignore directive');
  assert(!source.includes('__coverage__'), 'Already instrumented source');
  // Istanbul hashes AST metadata. Bind its runtime key to the original bytes too.
  const coverageKey = relative + '#sha256=' + digest(source);
  const tool = createInstrumenter({
    esModules: relative.endsWith('.esm.js'), compact: false, preserveComments: true,
    coverageVariable: '__coverage__', coverageGlobalScope: 'globalThis',
    coverageGlobalScopeFunc: false, produceSourceMap: false,
    // Odoo 18 rjsmin removes the required space in decimal numeric member access.
    // Hex integers preserve its semantics through that native asset minifier.
    generatorOpts: relative.includes('/static/src/lib/')
      ? { jsescOption: { numbers: 'hexadecimal' } } : {},
  });
  let generated = tool.instrumentSync(source, coverageKey);
  // Receipts and browser snapshots use JSON, which omits undefined locations.
  const seed = JSON.parse(JSON.stringify(tool.lastFileCoverage()));
  const initial = readInitialCoverage(generated);
  assert(initial && initial.path === coverageKey && initial.gcv === '__coverage__');
  for (const field of ['statementMap', 'fnMap', 'branchMap', 's', 'f', 'b']) {
    assert.deepEqual(JSON.parse(JSON.stringify(initial.coverageData[field])), seed[field], field);
  }
  assert([...Object.values(seed.s), ...Object.values(seed.f), ...Object.values(seed.b).flat()]
    .every(value => value === 0), 'Zero seed contains a hit');
  const header = source.match(/^\s*(\/\*\*\s*@odoo-module[^]*?\*\/)/);
  if (header && !generated.trimStart().startsWith(header[1])) generated = header[1] + '\n' + generated;
  return { generated, record: {
    originalSha256: digest(original), sourceSha256: digest(source), coverageKey,
    instrumentedSha256: digest(generated), hash: initial.hash, seed,
    provenance: relative.includes('/static/src/lib/') ? 'modified vendored SDK; included' : 'owned module',
  } };
}

function instrument(repository, root, destination) {
  assert(Object.hasOwn(inventory, repository), 'Unknown repository');
  root = fs.realpathSync(root);
  fs.mkdirSync(destination, { recursive: true });
  assert(!fs.existsSync(path.join(destination, 'inventory.json')), 'Receipt already exists');
  const records = {};
  for (const relative of inventory[repository]) {
    const filename = ownedFile(root, relative);
    const original = fs.readFileSync(filename);
    const { generated, record } = prepare(relative, original);
    fs.writeFileSync(path.join(destination, digest(relative) + '.original.js'), original);
    records[relative] = record;
    fs.writeFileSync(filename, generated);
  }
  fs.writeFileSync(path.join(destination, 'inventory.json'), JSON.stringify({ repository, files: records }, null, 2));
  return records;
}

if (require.main === module) {
  assert.equal(process.argv.length, 5, 'Usage: instrument.cjs repository source-root receipt-directory');
  instrument(...process.argv.slice(2));
}
module.exports = { instrument, inventory, prepare, ownedFile, digest };
