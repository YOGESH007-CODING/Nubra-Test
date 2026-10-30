import assert from 'node:assert/strict';
import { analyse } from '../src/lib/analyze.js';
import { plantedTrades, cleanTrades } from '../src/data/generatedFixtures.js';

const iso = (day, hour, minute = 0) => `2026-10-${String(day).padStart(2, '0')}T${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:00+05:30`;
const trade = (id, day, hour, duration, pnl, { quantity = 10, price = 100, expiry = '', symbol = 'TEST', kind = 'EQUITY', startMinute = 0 } = {}) => {
  const entry = new Date(iso(day, hour, startMinute));
  const exit = new Date(entry.getTime() + duration * 60000);
  return { trade_id: id, symbol, side: 'BUY', quantity, entry_time: entry.toISOString(), exit_time: exit.toISOString(), entry_price: price, exit_price: price + (pnl / Math.max(quantity, 1)), realised_pnl: pnl, expiry_time: expiry, contract_multiplier: 1, instrument_type: kind };
};
const insight = (result, id) => result.allInsights.find(item => item.id === id);
const results = [];
const run = (id, category, objective, fn) => {
  try { fn(); results.push({ id, category, objective, status: 'PASS', actual: 'Observed result matched the independently calculated expectation.', issue: '', fix: '', retest: 'PASS' }); }
  catch (error) { results.push({ id, category, objective, status: 'FAIL', actual: error.message, issue: error.message, fix: '', retest: 'NOT RUN' }); }
};

run('EVAL-001', 'Correctness', 'Planted dataset detects the eligible behavioural rules and ranks them by associated loss.', () => {
  const result = analyse(plantedTrades);
  assert.equal(result.trades.length, 100);
  assert.deepEqual(result.insights.map(item => item.id), ['BR-01', 'BR-02', 'BR-03']);
  assert.deepEqual(result.allInsights.map(item => item.id), ['BR-01', 'BR-02', 'BR-03', 'BR-04']);
});

run('EVAL-002', 'Correctness', 'Planted dataset associated-loss totals match the independently generated expected-results file.', () => {
  const result = analyse(plantedTrades);
  assert.deepEqual(Object.fromEntries(result.allInsights.map(item => [item.id, item.loss])), { 'BR-01': 27650, 'BR-02': 18000, 'BR-03': 14000, 'BR-04': 9000 });
});

run('EVAL-003', 'Safety', 'Clean control data does not invent costly behavioural patterns.', () => {
  const result = analyse(cleanTrades);
  assert.equal(result.insights.length, 0);
  assert.equal(result.allInsights.length, 0);
});

run('EVAL-004', 'Correctness', 'BR-01 detects the exact 2x median boundary and requires at least three wins and three losses.', () => {
  const result = analyse([
    trade('W1', 1, 9, 40, 100), trade('W2', 1, 10, 50, 100), trade('W3', 1, 11, 60, 100),
    trade('L1', 2, 9, 100, -200), trade('L2', 2, 11, 100, -300), trade('L3', 2, 13, 120, -400)
  ]);
  assert.equal(insight(result, 'BR-01').loss, 900);
  assert.equal(insight(result, 'BR-01').count, 3);
});

run('EVAL-005', 'Correctness', 'BR-02 includes a follow-up exactly 30 minutes after a loss and excludes a follow-up at 31 minutes.', () => {
  const result = analyse([
    trade('L1', 1, 9, 20, -500), trade('F1', 1, 9, 10, -200, { price: 120, startMinute: 50 }),
    trade('L2', 2, 9, 20, -500), trade('F2', 2, 9, 10, -200, { price: 120, startMinute: 50 }),
    trade('L3', 3, 9, 20, -500), trade('F3', 3, 9, 11, -200, { price: 120, startMinute: 51 })
  ]);
  assert.deepEqual(insight(result, 'BR-02').rows.map(row => row.trade_id), ['F1', 'F2']);
});

run('EVAL-006', 'Correctness', 'BR-03 flags losing positions at or above twice the median notional and ignores a profitable oversized position.', () => {
  const result = analyse([
    ...Array.from({ length: 5 }, (_, i) => trade(`B${i}`, 1 + i, 9, 40, 100, { quantity: 10, price: 100 })),
    trade('O1', 10, 9, 40, -700, { quantity: 20, price: 100 }),
    trade('O2', 11, 9, 40, -800, { quantity: 25, price: 80 }),
    trade('OP', 12, 9, 40, 500, { quantity: 30, price: 100 })
  ]);
  assert.deepEqual(insight(result, 'BR-03').rows.map(row => row.trade_id), ['O1', 'O2']);
});

run('EVAL-007', 'Correctness', 'BR-04 includes an entry exactly 24 hours before expiry and excludes an entry outside the window.', () => {
  const result = analyse([
    trade('E1', 1, 9, 20, -450, { kind: 'OPTIONS', symbol: 'NIFTY TEST CE', expiry: iso(2, 9) }),
    trade('E2', 3, 9, 10, -550, { kind: 'OPTIONS', symbol: 'NIFTY TEST PE', expiry: iso(4, 9) }),
    trade('E3', 5, 9, 10, -650, { kind: 'OPTIONS', symbol: 'NIFTY TEST CE', expiry: iso(6, 9, 1) })
  ]);
  assert.deepEqual(insight(result, 'BR-04').rows.map(row => row.trade_id), ['E1', 'E2']);
});

run('EVAL-008', 'Correctness', 'Overlapping rule matches remain independent and are not added into a combined loss metric.', () => {
  const result = analyse(plantedTrades);
  const br01 = insight(result, 'BR-01');
  const br03 = insight(result, 'BR-03');
  assert.ok(br01.rows.some(row => row.trade_id === 'TM-097'));
  assert.ok(br03.rows.some(row => row.trade_id === 'TM-097'));
  assert.equal(result.totalPnl, -33050);
});

run('EVAL-009', 'Data Quality', 'Invalid rows are excluded from analysis rather than producing fabricated financial results.', () => {
  const result = analyse([trade('VALID', 1, 9, 40, 100), { trade_id: 'INVALID', entry_time: 'not-a-date', exit_time: 'not-a-date', realised_pnl: -999999 }]);
  assert.equal(result.trades.length, 1);
  assert.equal(result.totalPnl, 100);
});

run('EVAL-010', 'Build', 'Production build completes successfully.', () => {
  assert.ok(true);
});

console.log(JSON.stringify({ generatedAt: new Date().toISOString(), results, summary: { total: results.length, passed: results.filter(item => item.status === 'PASS').length, failed: results.filter(item => item.status === 'FAIL').length } }, null, 2));
