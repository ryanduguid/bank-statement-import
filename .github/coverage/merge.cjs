// Copyright 2026 Ryan Duguid
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

'use strict';

const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const coverage = require('istanbul-lib-coverage');
const report = require('istanbul-lib-report');
const reports = require('istanbul-reports');
const { inventory: subjects, prepare, ownedFile, digest } = require('./instrument.cjs');

function merge(repository, sourceRoot, inventoryFile, sessions, destination) {
  assert(Object.hasOwn(subjects, repository), 'Unknown repository');
  const receipt = JSON.parse(fs.readFileSync(inventoryFile));
  assert.equal(receipt.repository, repository);
  const inventory = receipt.files;
  assert.deepEqual(Object.keys(inventory).sort(), [...subjects[repository]].sort(), 'Incomplete inventory');
  const byKey = new Map();
  const result = coverage.createCoverageMap({});
  for (const relative of subjects[repository]) {
    const original = fs.readFileSync(ownedFile(path.dirname(inventoryFile), digest(relative) + '.original.js'));
    const expected = prepare(relative, original);
    assert.deepEqual(inventory[relative], expected.record, 'Source receipt mismatch: ' + relative);
    const served = fs.readFileSync(ownedFile(sourceRoot, relative));
    assert.equal(digest(served), expected.record.instrumentedSha256, 'Served source mismatch: ' + relative);
    byKey.set(expected.record.coverageKey, { relative, ...expected.record });
    result.addFileCoverage({ ...structuredClone(expected.record.seed), path: relative });
  }
  const filenames = fs.readdirSync(sessions);
  const major = repository === 'bank-statement-import' ? 18 : 19;
  const hooks = filenames.filter(name => /^installed-[1-9][0-9]*-odoo(18|19)\.txt$/.test(name));
  assert(hooks.length > 0, 'Missing native browser coverage hook receipt');
  for (const filename of hooks) {
    assert(filename.endsWith('-odoo' + major + '.txt'), 'Wrong native browser coverage hook receipt');
    assert.equal(fs.readFileSync(path.join(sessions, filename), 'utf8'),
      'Native Odoo ' + major + ' browser coverage hook installed\n', 'Invalid native browser coverage hook receipt');
  }
  const contexts = new Map();
  for (const filename of filenames.filter(name => name.endsWith('.json')).sort()) {
    const session = JSON.parse(fs.readFileSync(path.join(sessions, filename)));
    assert(!session.error, session.error);
    assert(typeof session.browser === 'string' && Number.isInteger(session.context));
    const key = JSON.stringify([session.browser, session.context]);
    const current = contexts.get(key) || {};
    assert(session.coverage && typeof session.coverage === 'object' && !Array.isArray(session.coverage));
    for (const [coverageKey, measured] of Object.entries(session.coverage)) {
      assert(byKey.has(coverageKey), 'Uninventoried coverage source: ' + coverageKey);
      const expected = byKey.get(coverageKey);
      const relative = expected.relative;
      assert.equal(measured.path, coverageKey);
      assert.equal(measured.hash, expected.hash);
      for (const field of ['statementMap', 'fnMap', 'branchMap']) assert.deepEqual(measured[field], expected.seed[field], field);
      const previous = current[relative] || { ...structuredClone(expected.seed), path: relative };
      for (const field of ['s', 'f', 'b']) {
        assert.deepEqual(Object.keys(measured[field]).sort(), Object.keys(previous[field]).sort(), field);
        for (const id of Object.keys(previous[field])) {
          const values = field === 'b' ? measured[field][id] : [measured[field][id]];
          const old = field === 'b' ? previous[field][id] : [previous[field][id]];
          assert(Array.isArray(values) && values.length === old.length);
          assert(values.every(value => Number.isSafeInteger(value) && value >= 0), 'Invalid counter');
          const maximum = values.map((value, index) => Math.max(value, old[index]));
          previous[field][id] = field === 'b' ? maximum : maximum[0];
        }
      }
      current[relative] = previous;
    }
    contexts.set(key, current);
  }
  for (const context of contexts.values()) result.merge(context);
  assert.deepEqual(result.files().sort(), Object.keys(inventory).sort());
  fs.mkdirSync(destination, { recursive: true });
  fs.writeFileSync(path.join(destination, 'coverage-final.json'), JSON.stringify(result.toJSON()));
  const context = report.createContext({ dir: destination, coverageMap: result });
  reports.create('lcovonly').execute(context);
  reports.create('json-summary').execute(context);
  return result;
}
if (require.main === module) {
  assert.equal(process.argv.length, 7, 'Usage: merge.cjs repository instrumented-source-root inventory-file session-directory output-directory');
  merge(...process.argv.slice(2));
}
module.exports = { merge };
