/**
 * BPMN Validation Script
 * Reads BPMN XML from stdin, outputs JSON { valid, errors }
 *
 * Usage: echo "<xml>" | node validate.js
 */

const BpmnModdle = require('bpmn-moddle');
const { Linter } = require('bpmnlint');
const NodeResolver = require('bpmnlint/lib/resolver/node-resolver');

async function validate(xml) {
  const result = { valid: false, errors: [] };

  // Step 1: Schema parsing
  const moddle = new BpmnModdle();
  let rootElement;
  try {
    const parsed = await moddle.fromXML(xml);
    rootElement = parsed.rootElement;
  } catch (err) {
    result.errors.push({ rule: 'xml-parse', message: err.message || String(err) });
    console.log(JSON.stringify(result));
    return;
  }

  // Step 2: bpmnlint structural checks
  try {
    const linter = new Linter({
      config: {
        extends: 'bpmnlint:recommended',
        rules: { 'no-bpmndi': 'error' }
      },
      resolver: new NodeResolver()
    });
    const lintResults = await linter.lint(rootElement);

    for (const [rule, issues] of Object.entries(lintResults)) {
      for (const issue of issues) {
        if (issue.category === 'error') {
          result.errors.push({
            rule,
            message: issue.message || issue.label || String(issue),
            id: issue.id || null
          });
        }
      }
    }
  } catch (err) {
    result.errors.push({ rule: 'lint-failure', message: err.message || String(err), id: null });
  }

  result.valid = result.errors.length === 0;
  console.log(JSON.stringify(result));
}

let xml = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { xml += chunk; });
process.stdin.on('end', () => {
  validate(xml.trim()).catch(err => {
    console.log(JSON.stringify({
      valid: false,
      errors: [{ rule: 'fatal', message: err.message || String(err) }]
    }));
  });
});
