from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv, statistics, json

IST = timezone(timedelta(hours=5, minutes=30))
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "datasets"
OUT.mkdir(parents=True, exist_ok=True)
FIELDS = ["trade_id","symbol","side","quantity","entry_time","exit_time","entry_price","exit_price","realised_pnl","expiry_time","contract_multiplier","instrument_type"]

def iso(dt): return dt.astimezone(IST).isoformat(timespec="seconds")
def row(i, entry, duration, symbol, qty, price, pnl, expiry="", kind="EQUITY", side="BUY", multiplier=1):
    exit_time = entry + timedelta(minutes=duration)
    # Synthetic price path is directionally plausible; pnl includes small synthetic costs.
    move = abs(pnl) / max(qty * multiplier, 1)
    exit_price = price + move if pnl >= 0 else max(price - move, 0.01)
    return {"trade_id": f"TM-{i:03d}", "symbol": symbol, "side": side, "quantity": qty,
            "entry_time": iso(entry), "exit_time": iso(exit_time), "entry_price": f"{price:.2f}",
            "exit_price": f"{exit_price:.2f}", "realised_pnl": f"{pnl:.2f}", "expiry_time": iso(expiry) if expiry else "",
            "contract_multiplier": multiplier, "instrument_type": kind}

def planted():
    rows, n = [], 1
    start = datetime(2026, 9, 1, 9, 20, tzinfo=IST)
    for i in range(90):
        day, slot = divmod(i, 4)
        entry = start + timedelta(days=day, minutes=slot * 180)
        is_win = i % 3 != 0
        duration = 25 + (i % 4) * 5 if is_win else 90 + (i % 4) * 10
        symbol = ["INFY", "RELIANCE", "TCS", "NIFTY 24200 CE"][i % 4]
        kind = "OPTIONS" if "NIFTY" in symbol else "EQUITY"
        expiry = entry + timedelta(days=4) if kind == "OPTIONS" else ""
        qty, price = (10 + i % 8, 1350 + (i % 9) * 80)
        pnl = 300 + (i % 7) * 35 if is_win else -(350 + (i % 8) * 30)
        rows.append(row(n, entry, duration, symbol, qty, price, pnl, expiry, kind)); n += 1

    # Three clean post-loss sequences with measurable follow-up losses.
    for j, day in enumerate([3, 11, 19]):
        base = start + timedelta(days=day, hours=0, minutes=10)
        rows.append(row(n, base, 45, "HDFCBANK", 12, 1600, -900)); n += 1
        rows.append(row(n, base + timedelta(minutes=60), 12, "NIFTY 24300 PE", 30, 140, -6000, base + timedelta(days=4), "OPTIONS")); n += 1

    # Two clearly oversized losing positions.
    for j, day in enumerate([7, 22]):
        entry = start + timedelta(days=day, hours=1, minutes=5)
        rows.append(row(n, entry, 70, "SYNTHBANK", 200, 4000 + j * 250, -7000, kind="EQUITY")); n += 1

    # Two losing options opened within 24 hours of expiry.
    for j, day in enumerate([14, 26]):
        expiry = start + timedelta(days=day, hours=6)
        entry = expiry - timedelta(hours=3)
        rows.append(row(n, entry, 35, f"NIFTY {24500+j*100} CE", 40, 180+j*15, -4500, expiry, "OPTIONS")); n += 1
    return rows

def clean():
    rows, start = [], datetime(2026, 9, 1, 9, 25, tzinfo=IST)
    for i in range(100):
        entry = start + timedelta(days=i // 4, minutes=(i % 4) * 120)
        win = i % 2 == 0
        duration = 42 + (i % 5) * 4
        symbol = ["INFY", "TCS", "RELIANCE", "HDFCBANK"][i % 4]
        pnl = 280 + (i % 5) * 25 if win else -(320 + (i % 5) * 22)
        rows.append(row(i + 1, entry, duration, symbol, 12 + i % 5, 1200 + (i % 7) * 90, pnl))
    return rows

def write_csv(name, rows):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    return path

def write_frontend_fixtures(planted_rows, clean_rows):
    path = ROOT / "src" / "data" / "generatedFixtures.js"
    path.write_text("export const plantedTrades = " + json.dumps(planted_rows, indent=2) + ";\n\nexport const cleanTrades = " + json.dumps(clean_rows, indent=2) + ";\n", encoding="utf-8")

def metrics(rows):
    parsed = []
    for r in rows:
        r = dict(r); r["entry"] = datetime.fromisoformat(r["entry_time"]); r["exit"] = datetime.fromisoformat(r["exit_time"])
        r["pnl"] = float(r["realised_pnl"]); r["qty"] = float(r["quantity"]); r["price"] = float(r["entry_price"]); r["mult"] = float(r["contract_multiplier"]); r["hold"] = (r["exit"]-r["entry"]).total_seconds()/60; r["notional"] = abs(r["qty"]*r["price"]*r["mult"]); r["expiry"] = datetime.fromisoformat(r["expiry_time"]) if r["expiry_time"] else None; parsed.append(r)
    wins = [r for r in parsed if r["pnl"] > 0]; losses = [r for r in parsed if r["pnl"] < 0]
    wm, lm = statistics.median([r["hold"] for r in wins]), statistics.median([r["hold"] for r in losses])
    br1 = [r for r in losses if r["hold"] >= 2 * wm]
    br2 = []
    for i, r in enumerate(parsed):
        prior = next((p for p in reversed(parsed[:i]) if p["exit"] <= r["entry"]), None)
        if prior and prior["pnl"] < 0 and (r["entry"]-prior["exit"]).total_seconds()/60 <= 30: br2.append(r)
    baseline = statistics.median([r["notional"] for r in parsed])
    br3 = [r for r in losses if r["notional"] >= 2*baseline]
    br4 = [r for r in losses if r["expiry"] and 0 <= (r["expiry"]-r["entry"]).total_seconds()/3600 <= 24]
    return {"BR-01": ("Holding losing trades longer", br1, "median losing holding duration >= 2 x median winning holding duration"), "BR-02": ("Trading shortly after a loss", br2, "next trade opens <= 30 minutes after prior loss closes"), "BR-03": ("Oversized positions", br3, "notional >= 2 x median comparable notional"), "BR-04": ("Trading close to expiry", br4, "opened <= 24 hours before expiry"), "_summary": (wins, losses, wm, lm, baseline)}

def write_expected(rows):
    m = metrics(rows); path = OUT / "trademirror_planted_habits_expected_results.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rule_id","pattern_name","matched_trade_ids","matched_trade_count","associated_loss_inr","threshold_used"]); writer.writeheader()
        for rule in ["BR-01","BR-02","BR-03","BR-04"]:
            name, matched, threshold = m[rule]; loss = sum(abs(r["pnl"]) for r in matched if r["pnl"] < 0)
            writer.writerow({"rule_id":rule,"pattern_name":name,"matched_trade_ids":";".join(r["trade_id"] for r in matched),"matched_trade_count":len(matched),"associated_loss_inr":round(loss),"threshold_used":threshold})
    return m

def write_report(m):
    wins, losses, wm, lm, baseline = m.pop("_summary")
    lines = ["TradeMirror planted habits validation report", "", f"Total trades: {len(wins)+len(losses)}", f"Winning trades: {len(wins)}", f"Losing trades: {len(losses)}", f"Median winning holding duration: {wm:.0f} minutes", f"Median losing holding duration: {lm:.0f} minutes", f"Median comparable trade notional: INR {baseline:,.0f}", f"Oversized losing trades: {len(m['BR-03'][1])}", f"Post-loss follow-up trades: {len(m['BR-02'][1])}", f"Losing trades opened within 24 hours of expiry: {len(m['BR-04'][1])}", "", "Pattern ranking by associated loss:"]
    ranking = []
    for rule, (name, matched, _) in m.items(): ranking.append((sum(abs(r["pnl"]) for r in matched if r["pnl"] < 0), rule, name, len(matched)))
    for loss, rule, name, count in sorted(ranking, reverse=True): lines.append(f"{rule} | {name} | INR {loss:,.0f} | {count} matched trades")
    (OUT / "trademirror_planted_habits_validation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

planted_rows = planted(); clean_rows = clean(); write_csv("trademirror_planted_habits.csv", planted_rows); write_csv("trademirror_clean_controls.csv", clean_rows); write_frontend_fixtures(planted_rows, clean_rows); write_expected(planted_rows); write_report(metrics(planted_rows))
print(f"Generated {len(planted_rows)} planted trades and {len(clean_rows)} clean controls in {OUT}")
