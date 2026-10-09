import {URL} from "node:url";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import {test} from "node:test";
import vm from "node:vm";

// Run with node --test account_statement_import_online_plaid/tests/js/plaid-polyfills.test.esm.js.
const filename = new URL(
  "../../static/src/lib/link/v2/stable/link-initialize.js",
  import.meta.url
);
const source = (await fs.readFile(filename, "utf8")).replace(/\r\n/g, "\n");
const startup = "return __webpack_require__((__webpack_require__.s = 1489));\n})([";
assert.equal(source.split(startup).length, 2, "review a changed SDK layout");
const begin = source.indexOf(startup) + startup.length - 1;
const end = source.lastIndexOf("]);");
assert.ok(end > begin);
assert.equal(source.slice(end + 3).trim(), "");
const modules = source.slice(begin, end + 1);

function context(capture) {
  const sandbox = vm.createContext({});
  vm.runInContext(
    `
        const modules = (${modules});
        if (!Array.isArray(modules) || modules.length !== 1519)
            throw new Error('review a changed SDK module array');
        for (const index of [66, 175, 204, 212])
            if (typeof modules[index] !== 'function')
                throw new Error('missing polyfill module');
        const cache = {};
        function load(index) {
            if (index === 175 && ${capture}) return (key, factory) => {
                globalThis.replaceFallback = factory(Symbol.replace,
                    String.prototype.replace, () => ({done: false}))[1];
            };
            if (cache[index]) return cache[index].exports;
            const module = cache[index] = {exports: {}};
            modules[index](module, module.exports, load);
            return module.exports;
        }
        globalThis.beforeStringReplace = String.prototype.replace;
        globalThis.beforeRegExpReplace = RegExp.prototype[Symbol.replace];
        load(66);
        `,
    sandbox,
    {timeout: 1000}
  );
  return sandbox;
}

const cases = [
  ["empty Unicode", "/(?:)/gu", "", "'-'", "-"],
  ["Unicode string end", "/(?:)/gu", "a", "'-'", "-a-"],
  ["upstream literal replacement", "/(?:)/gu", "abc", "'-'", "-a-b-c-"],
  ["callback replacement", "/(?:)/gu", "abc", "() => '-'", "-a-b-c-"],
  ["Unicode surrogate pair", "/(?:)/gu", "\uD83D\uDE00", "'-'", "-\uD83D\uDE00-"],
  ["ASCII surrogate pair", "/(?:)/g", "\uD83D\uDE00", "'-'", "-\uD83D-\uDE00-"],
  ["Unicode lone surrogate", "/(?:)/gu", "\uD800", "'-'", "-\uD800-"],
  ["non-global Unicode", "/(?:)/u", "", "'-'", "-"],
  ["empty ASCII", "/(?:)/g", "", "'-'", "-"],
  ["ordinary nonempty match", "/a/g", "ba", "'-'", "b-"],
];

for (const [name, regex, input, replacement, expected] of cases) {
  test(`bundled replacement fallback: ${name}`, () => {
    const sandbox = context(true);
    const result = vm.runInContext(
      `replaceFallback.call(${regex}, ${JSON.stringify(input)}, ${replacement})`,
      sandbox,
      {timeout: 250}
    );
    assert.equal(result, expected);
  });
}

test("bundled Unicode index advancement makes progress at the end", () => {
  const sandbox = context(true);
  for (const [input, index, unicode, expected] of [
    ["", 0, true, 1],
    ["abc", 3, true, 4],
    ["abc", 4, true, 5],
    ["\uD83D\uDE00", 0, true, 2],
    ["\uD83D\uDE00", 0, false, 1],
    ["\uD800", 0, true, 1],
  ]) {
    assert.equal(
      vm.runInContext(
        `load(212)(${JSON.stringify(input)}, ${index}, ${unicode})`,
        sandbox,
        {timeout: 250}
      ),
      expected
    );
  }
});

test("normal bundled dispatch preserves conforming native replacement", () => {
  const sandbox = context(false);
  assert.equal(
    vm.runInContext(
      "beforeStringReplace === String.prototype.replace && " +
        "beforeRegExpReplace === RegExp.prototype[Symbol.replace]",
      sandbox,
      {timeout: 250}
    ),
    true
  );
  assert.equal(
    vm.runInContext("'a'.replace(/(?:)/gu, '-')", sandbox, {timeout: 250}),
    "-a-"
  );
});
