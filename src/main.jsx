import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import Papa from 'papaparse';
import { analyse, formatINR } from './lib/analyze';
import { plantedTrades, cleanTrades } from './data/generatedFixtures';
import './styles.css';

const safety = 'For demo purposes only. Not investment advice.';

const timelineDate = date => date.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
const timelineLabel = date => date.toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata', day: 'numeric', month: 'short' });

function BehaviourTimeline({ result, onOpenEvent }) {
  const events = result.allInsights.flatMap(insight => insight.rows.map(row => ({
    id: `${insight.id}-${row.trade_id}`,
    ruleId: insight.id,
    ruleTitle: insight.title,
    row,
    date: timelineDate(row.entry),
    priorLoss: row.priorLoss
  }))).sort((a, b) => a.row.entry - b.row.entry || a.id.localeCompare(b.id));
  const dates = [...new Set(events.map(event => event.date))];
  const [selectedDate, setSelectedDate] = useState(dates[0]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const activeDate = dates.includes(selectedDate) ? selectedDate : dates[0];
  const dayEvents = events.filter(event => event.date === activeDate);
  const clusterCount = events.filter(event => event.date === activeDate).length;

  return <section className="timeline-section"><div className="section-head"><div><h2>Behaviour timeline</h2><p className="section-subtitle">Detected events across the review period</p></div><span>{events.length} events</span></div><div className="timeline-rail" role="list" aria-label="Detected behaviour dates">{dates.map(date => { const count = events.filter(event => event.date === date).length; return <button key={date} className={`date-node ${date === activeDate ? 'active' : ''} ${count > 1 ? 'cluster' : ''}`} onClick={() => { setSelectedDate(date); setSelectedEvent(null); }} role="listitem" aria-label={`${timelineLabel(new Date(`${date}T12:00:00`))}, ${count} detected event${count > 1 ? 's' : ''}`}><span>{timelineLabel(new Date(`${date}T12:00:00`))}</span><strong>{count}</strong></button>; })}</div><div className="timeline-detail"><div className="timeline-detail-head"><div><p className="label">Selected date</p><h3>{timelineLabel(new Date(`${activeDate}T12:00:00`))}</h3></div><span>{clusterCount > 1 ? `${clusterCount} events · cluster` : `${clusterCount} event`}</span></div>{dayEvents.length ? <div className="event-list">{dayEvents.map(event => <button key={event.id} className={`event-row ${selectedEvent === event.id ? 'selected' : ''}`} onClick={() => setSelectedEvent(selectedEvent === event.id ? null : event.id)}><span className="event-marker">{event.ruleId.replace('BR-', '')}</span><span className="event-copy"><strong>{event.ruleTitle}</strong><small>{event.row.trade_id} · {event.row.symbol} · {event.row.entry.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })} · {event.row.realised_pnl < 0 ? '-' : '+'}{formatINR(event.row.realised_pnl)}</small></span><span className="event-rule">{selectedEvent === event.id ? '−' : '+'}</span>{selectedEvent === event.id && <span className="event-detail">{event.ruleId === 'BR-02' && event.priorLoss ? `Follow-up opened ${event.elapsed} minutes after ${event.priorLoss.trade_id} closed. ` : ''}Matched rule: {event.ruleTitle}. <button className="inline-link" onClick={e => { e.stopPropagation(); onOpenEvent(event.ruleId); }}>View evidence</button></span>}</button>)}</div> : <p className="timeline-empty">No detected pattern events on this date.</p>}</div><p className="timeline-note">Clusters group multiple observed events on a date; they are not a severity score or a causal claim.</p></section>;
}

function App() {
  const [review, setReview] = useState(null);
  const [demoChoice, setDemoChoice] = useState('planted');
  const [source, setSource] = useState('demo');
  const [expanded, setExpanded] = useState(null);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState('');
  const result = useMemo(() => review ? analyse(review) : null, [review]);
  useEffect(() => {
    if (!expanded) return;
    requestAnimationFrame(() => document.querySelector('.insight.open')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }, [expanded]);

  const startDemo = (choice = demoChoice) => { setDemoChoice(choice); setSource(choice === 'clean' ? 'clean controls' : 'planted habits'); setError(''); setSelected(null); setExpanded(null); setReview(choice === 'clean' ? cleanTrades : plantedTrades); };
  const onFile = event => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) { setError('Please choose a CSV file.'); return; }
    Papa.parse(file, { header: true, skipEmptyLines: true, complete: ({ data, errors }) => {
      if (errors.length || !data.length) { setError('We could not read this file. Check the CSV and try again.'); return; }
      const required = ['entry_time', 'exit_time', 'realised_pnl'];
      const keys = Object.keys(data[0]).map(key => key.trim());
      if (!required.every(field => keys.includes(field))) { setError('Missing required columns: entry_time, exit_time and realised_pnl.'); return; }
      setSource(file.name); setError(''); setSelected(null); setExpanded(null); setReview(data);
    } });
  };

  const reset = () => { setReview(null); setSource('demo'); setError(''); setSelected(null); setExpanded(null); };

  if (!result) return <main className="shell start-shell"><div className="brand"><span className="brand-mark">TM</span><span>TradeMirror</span></div><section className="hero"><p className="eyebrow">POST-TRADE REVIEW</p><h1>Understand the patterns behind your trading.</h1><p className="hero-copy">Turn a month of completed trades into a short, evidence-backed review of the behaviours most associated with your losses.</p><div className="demo-picker"><p className="label">Choose a preloaded demo</p><div className="dataset-options"><button className={demoChoice === 'planted' ? 'dataset-option selected' : 'dataset-option'} onClick={() => setDemoChoice('planted')}><strong>Planted habits</strong><span>100 trades · exercises all four rules</span></button><button className={demoChoice === 'clean' ? 'dataset-option selected' : 'dataset-option'} onClick={() => setDemoChoice('clean')}><strong>Clean controls</strong><span>100 trades · should surface no patterns</span></button></div></div><div className="actions"><button className="primary" onClick={() => startDemo()}>Explore selected demo <span>→</span></button><label className="secondary">Upload CSV<input type="file" accept=".csv,text/csv" onChange={onFile} /></label></div>{error && <p className="error">{error}</p>}<p className="safety">{safety}</p></section><section className="principles"><div><strong>Observable</strong><span>Sequences, not intent.</span></div><div><strong>Evidence-backed</strong><span>Every insight traces to trades.</span></div><div><strong>One minute</strong><span>Only the top 2–3 patterns.</span></div></section></main>;

  return <main className="shell review-shell"><header className="topbar"><div className="brand"><span className="brand-mark">TM</span><span>TradeMirror</span></div><button className="text-button" onClick={reset}>New review <span>↗</span></button></header><div className="review-heading"><div><p className="eyebrow">MONTHLY REVIEW · {source === 'demo' ? 'DEMO DATA' : source.toUpperCase()}</p><h1>Your trading patterns</h1><p>Review what repeated, how much loss was associated with it, and what to monitor next.</p></div><div className="pnl"><span>Net P&amp;L</span><strong className={result.totalPnl >= 0 ? 'positive' : 'negative'}>{result.totalPnl < 0 ? '-' : ''}{formatINR(result.totalPnl)}</strong><small>{result.trades.length} trades reviewed</small></div></div><div className="notice"><span>i</span><span>These are observed associations, not proof that a behaviour caused a loss.</span></div>{result.insights.length ? <section className="insights"><div className="section-head"><h2>Your biggest behavioural patterns</h2><span>{result.insights.length} found</span></div>{result.insights.map((insight, index) => <article className={`insight ${expanded === insight.id ? 'open' : ''}`} key={insight.id}><button className="insight-main" onClick={() => setExpanded(expanded === insight.id ? null : insight.id)}><span className="rank">0{index + 1}</span><span className="insight-icon">{insight.icon}</span><span className="insight-title"><strong>{insight.title}</strong><em>{insight.summary}</em></span><span className="insight-loss"><strong>{formatINR(insight.loss)}</strong><small>associated losses · {insight.count} trades</small></span><span className="chevron">{expanded === insight.id ? '−' : '+'}</span></button>{expanded === insight.id && <div className="evidence"><div><p className="label">What the data shows</p><ul>{insight.evidence.map(item => <li key={item}>{item}</li>)}</ul></div><div><p className="label">Try monitoring this next month</p><p className="improvement">{insight.improvement}</p></div><div className="evidence-table"><p className="label">Matched trades</p>{insight.rows.slice(0, 6).map(row => <div className="trade-row" key={row.trade_id}><span>{row.trade_id} · {row.symbol}</span><strong className={row.realised_pnl < 0 ? 'negative' : 'positive'}>{row.realised_pnl < 0 ? '-' : '+'}{formatINR(row.realised_pnl)}</strong></div>)}</div></div>}</article>)}</section> : <section className="empty"><div className="empty-icon">✓</div><h2>No qualifying patterns found</h2><p>This review did not surface enough evidence for one of the behavioural rules. That is a valid result - TradeMirror will not invent a problem.</p></section>}{result.allInsights.length > 0 && <BehaviourTimeline result={result} onOpenEvent={ruleId => setExpanded(ruleId)} />}<footer className="review-footer"><span>{safety}</span><span>Analysis runs in your browser. Your file is not uploaded.</span></footer></main>;
}

createRoot(document.getElementById('root')).render(<App />);
