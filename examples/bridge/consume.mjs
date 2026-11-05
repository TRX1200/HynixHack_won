// Synthetic Python -> JSON -> JavaScript boundary example. No network or browser control.
import fs from 'node:fs';

function keys(x, expected) {
  if (x === null || typeof x !== 'object' || Array.isArray(x) ||
      JSON.stringify(Object.keys(x).sort()) !== JSON.stringify([...expected].sort())) {
    throw new Error('Unexpected object fields.');
  }
}
function number(x) {
  if (typeof x !== 'number' || !Number.isFinite(x)) throw new Error('Finite number required.');
  return x;
}
export function validateResult(x) {
  keys(x, ['schema_version','unit','items','count_total','count_used','mean']);
  if (x.schema_version !== '1.0' || x.unit !== 'degC') throw new Error('Version/unit mismatch.');
  if (!Array.isArray(x.items) || x.items.length < 1 || x.items.length > 10000) throw new Error('Invalid row count.');
  if (!Number.isSafeInteger(x.count_total) || !Number.isSafeInteger(x.count_used)) throw new Error('Integer counts required.');
  const ids = new Set(); const values = [];
  for (const row of x.items) {
    keys(row, ['id','value']);
    if (typeof row.id !== 'string' || !row.id.trim() || [...row.id].length > 128 || ids.has(row.id)) {
      throw new Error('Unique nonempty string IDs required.');
    }
    ids.add(row.id);
    if (row.value !== null) {
      const v = number(row.value);
      if (v < -273.15 || v > 1000000) throw new Error('Temperature outside example range.');
      values.push(v);
    }
  }
  if (x.count_total !== x.items.length || x.count_used !== values.length) throw new Error('Count mismatch.');
  if (values.length === 0) {
    if (x.mean !== null) throw new Error('Missing-only input must have null mean.');
  } else {
    // Kahan summation reduces error; displayed rounding is not used for validation.
    let sum = 0, correction = 0;
    for (const v of values) { const y = v - correction; const t = sum + y; correction = (t - sum) - y; sum = t; }
    const expected = sum / values.length;
    const mean = number(x.mean);
    if (Math.abs(mean-expected) > Math.max(1e-10, 1e-10*Math.max(Math.abs(mean), Math.abs(expected)))) {
      throw new Error('Mean mismatch.');
    }
  }
  return x;
}
try {
  if (process.argv.length !== 3) throw new Error('Usage: node consume.mjs <producer-output.json>');
  const path = process.argv[2];
  if (!fs.statSync(path).isFile() || fs.statSync(path).size > 2000000) throw new Error('Input file too large or not a file.');
  const result = validateResult(JSON.parse(fs.readFileSync(path, 'utf8')));
  console.log(JSON.stringify({validated: true, unit: result.unit, mean: result.mean,
    count_used: result.count_used, count_total: result.count_total, ids: result.items.map(r => r.id)}));
} catch (e) { console.error(`ERROR: ${e.message}`); process.exitCode = 2; }
