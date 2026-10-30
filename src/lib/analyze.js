const median = values => {
  const sorted = [...values].sort((a, b) => a - b);
  if (!sorted.length) return null;
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

const money = value => Math.round(value);
const lossOn = rows => money(rows.reduce((sum, row) => sum + (row.realised_pnl < 0 ? Math.abs(row.realised_pnl) : 0), 0));
const minutesBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 60000);

export const normaliseTrades = rows => rows.map((row, index) => ({
  ...row,
  trade_id: row.trade_id || `ROW-${index + 1}`,
  quantity: Number(row.quantity),
  entry_price: Number(row.entry_price),
  realised_pnl: Number(row.realised_pnl),
  contract_multiplier: Number(row.contract_multiplier || 1),
  entry: new Date(row.entry_time),
  exit: new Date(row.exit_time),
  expiry: row.expiry_time ? new Date(row.expiry_time) : null
})).filter(row => row.entry instanceof Date && !Number.isNaN(row.entry) && row.exit instanceof Date && !Number.isNaN(row.exit) && row.exit >= row.entry && Number.isFinite(row.realised_pnl));

export function analyse(rows) {
  const trades = normaliseTrades(rows).sort((a, b) => a.entry - b.entry).map(row => ({ ...row, holdingMinutes: minutesBetween(row.entry, row.exit), notional: Math.abs(row.quantity * row.entry_price * row.contract_multiplier) }));
  const wins = trades.filter(t => t.realised_pnl > 0);
  const losses = trades.filter(t => t.realised_pnl < 0);
  const results = [];

  const winMedian = median(wins.map(t => t.holdingMinutes));
  const lossMedian = median(losses.map(t => t.holdingMinutes));
  if (winMedian && lossMedian && wins.length >= 3 && losses.length >= 3 && lossMedian >= winMedian * 2) {
    const matched = losses.filter(t => t.holdingMinutes >= winMedian * 2);
    results.push({ id: 'BR-01', title: 'Holding losing trades longer', icon: '↗', loss: lossOn(matched), count: matched.length, summary: `Losing trades were held ${Math.round((lossMedian / winMedian) * 10) / 10}× longer than winning trades.`, evidence: [`Median winning hold: ${winMedian} minutes`, `Median losing hold: ${lossMedian} minutes`, `${matched.length} losing trades matched the 2× rule`], rows: matched, improvement: 'Compare losing and winning holding times next month; consider documenting an exit rule before entry.' });
  }

  const followups = [];
  trades.forEach((trade, index) => {
    const prior = trades.slice(0, index).reverse().find(candidate => candidate.exit <= trade.entry);
    if (prior && prior.realised_pnl < 0 && minutesBetween(prior.exit, trade.entry) <= 30) followups.push({ ...trade, priorLoss: prior, elapsed: minutesBetween(prior.exit, trade.entry) });
  });
  if (followups.length >= 2 && lossOn(followups) > 0) results.push({ id: 'BR-02', title: 'Trading again after a loss', icon: '↻', loss: lossOn(followups), count: followups.length, summary: `${followups.length} trades opened within 30 minutes of a losing trade closing.`, evidence: followups.map(t => `${t.trade_id}: ${t.elapsed} minutes after ${t.priorLoss.trade_id}`), rows: followups, improvement: 'Record whether the next trade opened within 30 minutes after a loss and what independent reason supported it.' });

  const baseline = median(trades.map(t => t.notional).filter(Number.isFinite));
  const oversized = trades.filter(t => t.notional >= baseline * 2 && t.realised_pnl < 0);
  if (oversized.length >= 2 && baseline > 0) results.push({ id: 'BR-03', title: 'Oversized positions', icon: '▣', loss: lossOn(oversized), count: oversized.length, summary: `${oversized.length} losing trades were at least 2× the median position size.`, evidence: [`Median comparable notional: INR ${money(baseline).toLocaleString('en-IN')}`, `Threshold used: 2× median notional`, `${oversized.length} losing trades matched the size rule`], rows: oversized, improvement: 'Set a personal position-size limit before a session and review trades exceeding it.' });

  const nearExpiry = trades.filter(t => t.expiry && t.expiry >= t.entry && (t.expiry - t.entry) / 3600000 <= 24 && t.realised_pnl < 0);
  if (nearExpiry.length >= 2) results.push({ id: 'BR-04', title: 'Trading close to expiry', icon: '◷', loss: lossOn(nearExpiry), count: nearExpiry.length, summary: `${nearExpiry.length} losing trades opened within 24 hours of expiry.`, evidence: [`Window used: within 24 hours of expiry`, `${nearExpiry.length} losing trades matched the expiry rule`], rows: nearExpiry, improvement: 'Record why a trade was opened with less than one day to expiry and review that outcome separately.' });

  const rankedAll = results.sort((a, b) => b.loss - a.loss || b.count - a.count || a.id.localeCompare(b.id));
  return { trades, insights: rankedAll.slice(0, 3), allInsights: rankedAll, totalPnl: money(trades.reduce((sum, t) => sum + t.realised_pnl, 0)), period: trades.length ? `${trades[0].entry.toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}` : 'No review period' };
}

export const formatINR = value => `INR ${Math.abs(Math.round(value)).toLocaleString('en-IN')}`;
