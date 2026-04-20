/**
 * BPMN Validation Script
 * Step 1: Schema parsing via bpmn-moddle (catches malformed XML, missing IDs, bad refs)
 * Step 2: Model soundness via bpmnlint (catches missing start/end events, open gateways, etc.)
 *
 * Usage: echo "<bpmn-xml>" | node validate.js
 * Output: JSON { success, moddle_errors, lint_errors }
 */

const BpmnModdle = require('bpmn-moddle');
const { Linter } = require('bpmnlint');
const NodeResolver = require('bpmnlint/lib/resolver/node-resolver');

async function validate(xml) {
  const result = {
    success: false,
    moddle_errors: [],
    lint_errors: []
  };

  // --- Step 1: Schema parsing ---
  const moddle = new BpmnModdle();
  let rootElement;

  try {
    const parsed = await moddle.fromXML(xml);
    rootElement = parsed.rootElement;
    // bpmn-moddle may return non-fatal warnings — treat as informational only
  } catch (err) {
    result.moddle_errors = [err.message || String(err)];
    console.log(JSON.stringify(result));
    return;
  }

  // --- Step 2: Model soundness ---
  try {
    const linter = new Linter({
      config: {
        extends: 'bpmnlint:recommended',
        rules: {
          'no-bpmndi': 'error'
        }
      },
      resolver: new NodeResolver()
    });
    const lintResults = await linter.lint(rootElement);

    for (const [rule, issues] of Object.entries(lintResults)) {
      for (const issue of issues) {
        // Only collect errors, not warnings
        if (issue.category === 'error') {
          result.lint_errors.push({
            rule,
            message: issue.message || issue.label || String(issue),
            id: issue.id || null
          });
        }
      }
    }
    result.success = true;
  } catch (err) {
    // Linting failure is non-fatal — parsing already succeeded
    result.lint_errors = [{
      rule: 'lint-failure',
      message: err.message || String(err),
      id: null
    }];
    result.success = true;
  }

  console.log(JSON.stringify(result));
}

// Read BPMN XML from stdin
let xml = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { xml += chunk; });
process.stdin.on('end', () => {
  validate(xml.trim()).catch(err => {
    console.log(JSON.stringify({
      success: false,
      moddle_errors: [err.message || String(err)],
      lint_errors: []
    }));
  });
});
