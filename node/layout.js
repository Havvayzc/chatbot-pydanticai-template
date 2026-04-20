/**
 * BPMN Auto-Layout Script
 * Applies deterministic layout to a BPMN XML model (adds DI coordinates).
 * The LLM-generated XML contains only the process logic — no coordinates.
 * This script adds them so the diagram opens correctly in Camunda Modeler etc.
 *
 * Usage: echo "<bpmn-xml>" | node layout.js
 * Output: BPMN XML with layout (stdout) or error message (stderr, exit 1)
 */

const { layoutProcess } = require('bpmn-auto-layout');

let xml = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { xml += chunk; });
process.stdin.on('end', () => {
  layoutProcess(xml)
    .then(result => {
      process.stdout.write(result);
    })
    .catch(err => {
      process.stderr.write(err.message || String(err));
      process.exit(1);
    });
});
