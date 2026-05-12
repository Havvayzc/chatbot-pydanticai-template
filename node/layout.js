/**
 * Auto-Layout Script
 * Reads BPMN XML from stdin, applies bpmn-auto-layout, outputs result to stdout.
 *
 * Usage: echo "<xml>" | node layout.js
 */

const { layoutProcess } = require('bpmn-auto-layout');

let xml = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { xml += chunk; });
process.stdin.on('end', () => {
  layoutProcess(xml.trim())
    .then(result => {
      process.stdout.write(result);
    })
    .catch(err => {
      process.stderr.write('LAYOUT ERROR: ' + (err.message || String(err)));
      process.exit(1);
    });
});
