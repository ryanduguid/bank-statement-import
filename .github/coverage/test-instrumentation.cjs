// Copyright 2026 Ryan Duguid
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const vm = require('node:vm');
const { instrument, inventory } = require('./instrument.cjs');
const { merge } = require('./merge.cjs');

function fixture(t, source = '// A comment is not an executable statement.\n\nfunction branch(value) {\n  if (value) return 17;\n  return 29;\n}\n') {
  const base = fs.realpathSync(os.tmpdir());
  const root = fs.mkdtempSync(path.join(base, 'oca-coverage-test-'));
  t.after(() => {
    assert.equal(path.dirname(root), base);
    assert(path.basename(root).startsWith('oca-coverage-test-'));
    fs.rmSync(root, { recursive: true });
  });
  const copy = path.join(root, 'source');
  for (const relative of inventory['account-invoicing']) {
    fs.mkdirSync(path.dirname(path.join(copy, relative)), { recursive: true });
    fs.writeFileSync(path.join(copy, relative), source);
  }
  const receipts = path.join(root, 'receipts');
  const sessions = path.join(root, 'sessions');
  fs.mkdirSync(sessions);
  fs.writeFileSync(path.join(sessions, 'installed-1-odoo19.txt'), 'Native Odoo 19 browser coverage hook installed\n');
  return { root, copy, receipts, sessions };
}

test('unloaded originals retain real zero AST maps; repeated snapshots do not multiply hits', t => {
  const data = fixture(t);
  const records = instrument('account-invoicing', data.copy, data.receipts);
  const [loaded, unloaded] = inventory['account-invoicing'];
  const context = vm.createContext({});
  new vm.Script(fs.readFileSync(path.join(data.copy, loaded), 'utf8')).runInContext(context);
  assert.equal(new vm.Script('branch(true)').runInContext(context), 17);
  const observed = JSON.parse(JSON.stringify(context.__coverage__));
  for (const sequence of [1, 2]) fs.writeFileSync(path.join(data.sessions, sequence + '.json'),
    JSON.stringify({ browser: 'fixture', context: 1, coverage: observed }));
  const result = merge('account-invoicing', data.copy, path.join(data.receipts, 'inventory.json'), data.sessions, path.join(data.root, 'report'));
  const actual = result.fileCoverageFor(loaded).data;
  assert.deepEqual(actual.s, observed[records[loaded].coverageKey].s);
  assert(Object.values(actual.b).flat().includes(0), 'Uncalled branch must remain uncovered');
  assert(Object.values(result.fileCoverageFor(unloaded).data.s).every(count => count === 0));
  assert(!Object.values(records[loaded].seed.statementMap).some(item => item.start.line <= 2), 'Comments/blanks entered denominator');
  assert(fs.readFileSync(path.join(data.root, 'report/lcov.info'), 'utf8').includes('SF:' + unloaded));
});

test('ignore directives are refused instead of hiding source', t => {
  const data = fixture(t, '/* istanbul ignore next */\nfunction missing() { return 1; }\n');
  assert.throws(() => instrument('account-invoicing', data.copy, data.receipts), /ignore directive/);
});

test('leading Odoo annotation stays at the beginning of the served copy', t => {
  const data = fixture(t, '/** @odoo-module **/\nfunction value() { return 1; }\n');
  instrument('account-invoicing', data.copy, data.receipts);
  const text = fs.readFileSync(path.join(data.copy, inventory['account-invoicing'][0]), 'utf8');
  assert(text.startsWith('/** @odoo-module **/'));
});

for (const invalid of ['hash', 'map', 'path', 'counter']) test('rejects mismatched runtime ' + invalid, t => {
  const data = fixture(t);
  const records = instrument('account-invoicing', data.copy, data.receipts);
  const filename = inventory['account-invoicing'][0];
  const measured = structuredClone(records[filename].seed);
  measured.hash = records[filename].hash;
  const values = { [records[filename].coverageKey]: measured };
  if (invalid === 'hash') measured.hash = 'different';
  if (invalid === 'map') measured.statementMap['0'].start.line += 1;
  if (invalid === 'path') { values['../outside.js'] = measured; delete values[records[filename].coverageKey]; }
  if (invalid === 'counter') measured.s['0'] = -1;
  fs.writeFileSync(path.join(data.sessions, 'bad.json'), JSON.stringify({ browser: 'fixture', context: 1, coverage: values }));
  assert.throws(() => merge('account-invoicing', data.copy, path.join(data.receipts, 'inventory.json'), data.sessions, path.join(data.root, 'report')));
});

function observe(data) {
  const loaded = inventory['account-invoicing'][0];
  const context = vm.createContext({});
  new vm.Script(fs.readFileSync(path.join(data.copy, loaded), 'utf8')).runInContext(context);
  new vm.Script('branch(true)').runInContext(context);
  return JSON.parse(JSON.stringify(context.__coverage__));
}

test('cumulative snapshots use maxima while independent documents add counters', t => {
  const data = fixture(t);
  const records = instrument('account-invoicing', data.copy, data.receipts);
  const relative = inventory['account-invoicing'][0];
  const key = records[relative].coverageKey;
  const observed = observe(data);
  const statement = Object.keys(observed[key].s).find(id => observed[key].s[id] > 0);
  assert(statement !== undefined);
  for (const [sequence, context, count] of [[1, 1, 2], [2, 1, 5], [3, 2, 3]]) {
    const snapshot = structuredClone(observed);
    snapshot[key].s[statement] = count;
    fs.writeFileSync(path.join(data.sessions, sequence + '.json'),
      JSON.stringify({ browser: 'fixture', context, coverage: snapshot }));
  }
  const result = merge('account-invoicing', data.copy, path.join(data.receipts, 'inventory.json'), data.sessions, path.join(data.root, 'report'));
  assert.equal(result.fileCoverageFor(relative).data.s[statement], 8);
});

test('an unloaded original cannot be removed from the denominator', t => {
  const data = fixture(t);
  instrument('account-invoicing', data.copy, data.receipts);
  const filename = path.join(data.receipts, 'inventory.json');
  const receipt = JSON.parse(fs.readFileSync(filename));
  delete receipt.files[inventory['account-invoicing'][1]];
  fs.writeFileSync(filename, JSON.stringify(receipt));
  fs.writeFileSync(path.join(data.sessions, 'observed.json'), JSON.stringify({ browser: 'fixture', context: 1, coverage: observe(data) }));
  assert.throws(() => merge('account-invoicing', data.copy, filename, data.sessions, path.join(data.root, 'report')));
});

test('same-shaped foreign source cannot supply execution hits', t => {
  const original = fixture(t, 'function branch(value) { if (value) return 17; return 29; }\n');
  const foreign = fixture(t, 'function branch(value) { if (value) return 19; return 29; }\n');
  instrument('account-invoicing', original.copy, original.receipts);
  instrument('account-invoicing', foreign.copy, foreign.receipts);
  fs.writeFileSync(path.join(original.sessions, 'foreign.json'), JSON.stringify({ browser: 'fixture', context: 1, coverage: observe(foreign) }));
  assert.throws(() => merge('account-invoicing', original.copy, path.join(original.receipts, 'inventory.json'), original.sessions, path.join(original.root, 'report')));
});

for (const which of ['retained original', 'served copy']) test('rejects a changed ' + which, t => {
  const data = fixture(t);
  instrument('account-invoicing', data.copy, data.receipts);
  fs.writeFileSync(path.join(data.sessions, 'observed.json'), JSON.stringify({ browser: 'fixture', context: 1, coverage: observe(data) }));
  const filename = which === 'retained original'
    ? fs.readdirSync(data.receipts).find(name => name.endsWith('.original.js'))
    : inventory['account-invoicing'][0];
  fs.appendFileSync(path.join(which === 'retained original' ? data.receipts : data.copy, filename), '\nthrow Error("changed source");\n');
  assert.throws(() => merge('account-invoicing', data.copy, path.join(data.receipts, 'inventory.json'), data.sessions, path.join(data.root, 'report')));
});

test('a missing browser hook cannot produce an apparently valid zero report', t => {
  const data = fixture(t);
  instrument('account-invoicing', data.copy, data.receipts);
  fs.unlinkSync(path.join(data.sessions, 'installed-1-odoo19.txt'));
  assert.throws(() => merge('account-invoicing', data.copy, path.join(data.receipts, 'inventory.json'), data.sessions, path.join(data.root, 'report')), /hook receipt/);
});

test('a valid hook without browser documents retains the full zero inventory', t => {
  const data = fixture(t);
  instrument('account-invoicing', data.copy, data.receipts);
  const result = merge('account-invoicing', data.copy, path.join(data.receipts, 'inventory.json'), data.sessions, path.join(data.root, 'report'));
  assert.deepEqual(result.files().sort(), [...inventory['account-invoicing']].sort());
  for (const filename of result.files()) {
    const counts = result.fileCoverageFor(filename).data;
    assert(Object.values(counts.s).every(value => value === 0));
    assert(Object.values(counts.f).every(value => value === 0));
    assert(Object.values(counts.b).flat().every(value => value === 0));
  }
});
