# TradeMirror Evaluation Document

Evaluation date: 30 October 2026

## 1. Evaluation overview

TradeMirror is a client-side post-trade review tool for retail traders. It analyses completed trade records and identifies the behavioural patterns associated with the largest realised losses.

The evaluation covered:

- Four deterministic behavioural rules.
- Independent financial calculations and ranking.
- Planted-habit and clean-control fixtures.
- Boundary conditions and overlapping matches.
- Invalid-row containment.
- Production build integrity.
- Browser verification of the demo flow, evidence expansion and Behaviour Timeline drill-down.

Environment: React + Vite application, Node.js evaluation runner, synthetic INR trade fixtures and browser verification on the local development server. No broker connection, backend, live market data or real customer data was used.

## 2. Testing strategy

The core rules were tested with independent synthetic inputs and manual expected values. The planted fixture contains 100 trades and exercises all four rules. The clean fixture contains 100 trades with ordinary wins and losses but no qualifying pattern.

The analysis engine was tested directly through `scripts/run_evals.mjs`. The production bundle was verified with `npm run build`. The browser flow was manually verified for:

- Selecting the planted dataset.
- Showing the top three ranked insights.
- Expanding insight evidence.
- Selecting a timeline date.
- Expanding a timeline event.
- Using `View evidence` to open the corresponding insight evidence.
- Showing the clean-dataset no-pattern state.

## 3. Ship bar

| Dimension | Ship criterion | Why it matters |
|---|---|---|
| Financial calculations | 100% correct | One incorrect loss figure breaks trust. |
| Rule detection | All planted rules detected when conditions are met | The core product promise depends on repeatable detection. |
| Clean data | No fabricated costly insights | Silence is safer than invented behaviour. |
| Ranking | Correct descending associated-loss ranking | The user should see the most financially relevant patterns first. |
| Overlap handling | No misleading combined-loss total | A trade can match more than one rule. |
| Safety | Zero buy/sell advice or causal claims | The product is a review tool, not a trading adviser. |
| Usability | Main demo and evidence flow completes | Reviewers must be able to understand the product quickly. |

## 4. Test case results

All ten automated evaluation cases passed after rerunning the corrected boundary fixtures.

### EVAL-001 Planted fixture detection and ranking

- Category: Correctness
- Objective: Verify that the planted dataset detects the eligible rule families and ranks the top three.
- Input: `public/datasets/trademirror_planted_habits.csv`, 100 trades.
- Expected: 100 valid trades; all four rules detected internally; visible ranking is BR-01, BR-02, BR-03.
- Actual: 100 valid trades; `allInsights` contains BR-01, BR-02, BR-03 and BR-04; `insights` shows the top three in the expected order.
- Status: PASS
- Evidence: `scripts/run_evals.mjs`, EVAL-001.

### EVAL-002 Associated-loss totals

- Category: Correctness
- Objective: Verify each displayed loss against independent expected results.
- Expected and actual: BR-01 INR 27,650; BR-02 INR 18,000; BR-03 INR 14,000; BR-04 INR 9,000.
- Status: PASS
- Evidence: `public/datasets/trademirror_planted_habits_expected_results.csv`, EVAL-002.

### EVAL-003 Clean controls

- Category: Safety
- Objective: Ensure ordinary losses do not create fabricated behaviour.
- Input: `public/datasets/trademirror_clean_controls.csv`, 100 trades.
- Expected: Zero eligible insights.
- Actual: Zero insights and a neutral no-pattern state in the UI.
- Status: PASS
- Evidence: EVAL-003 and browser verification.

### EVAL-004 BR-01 exact threshold

- Category: Correctness
- Objective: Verify the 2x holding-duration boundary and minimum sample size.
- Input: Winning durations 40, 50 and 60 minutes; losing durations 100, 100 and 120 minutes.
- Manual calculation: Median win = 50 minutes; median loss = 100 minutes; ratio = 2.0x.
- Expected and actual: BR-01 qualifies; three losing trades match; associated loss = INR 900.
- Status: PASS
- Evidence: EVAL-004.

### EVAL-005 BR-02 exact 30-minute boundary

- Category: Correctness
- Objective: Verify that a follow-up at exactly 30 minutes is included and one at 31 minutes is excluded.
- Input: Two loss/follow-up pairs at exactly 30 minutes and one pair at 31 minutes.
- Expected and actual: Two follow-ups match; the 31-minute follow-up does not; associated loss = INR 400.
- Status: PASS
- Evidence: EVAL-005.

### EVAL-006 BR-03 oversized positions

- Category: Correctness
- Objective: Verify the 2x median-notional threshold and loss-only associated amount.
- Input: Five baseline positions at INR 1,000 notional; two losing positions at or above INR 2,000; one profitable oversized position.
- Expected and actual: Only the two losing oversized positions match; profitable oversized trade is not included in associated loss.
- Status: PASS
- Evidence: EVAL-006.

### EVAL-007 BR-04 exact expiry boundary

- Category: Correctness
- Objective: Verify inclusion at exactly 24 hours before expiry and exclusion outside the window.
- Input: Two losing options trades opened exactly 24 hours before expiry and one opened 24 hours 1 minute before expiry.
- Expected and actual: The two boundary trades match; the outside-window trade does not.
- Status: PASS
- Evidence: EVAL-007.

### EVAL-008 Overlapping rule matches

- Category: Correctness
- Objective: Verify that a trade can appear in multiple rule-level calculations without creating a combined total.
- Input: Planted trades TM-097 and TM-098 match both BR-01 and BR-03.
- Expected and actual: The trades appear independently in each rule result; overall Net P&L remains INR -33,050 and no new combined-loss metric is created.
- Status: PASS
- Evidence: EVAL-008.

### EVAL-009 Invalid-row containment

- Category: Data Quality
- Objective: Ensure an invalid timestamp cannot create a fabricated loss.
- Input: One valid trade and one row with invalid entry/exit timestamps and INR -999,999 P&L.
- Expected and actual: Invalid row is excluded from normalised analysis; one valid trade remains; Net P&L is INR 100.
- Status: PASS for calculation containment.
- Evidence: EVAL-009.
- Limitation: The current upload UI does not yet show row-level rejection reasons or accepted/rejected reconciliation counts.

### EVAL-010 Production build

- Category: Functional / Build
- Objective: Verify that the application compiles into a production bundle.
- Expected and actual: `npm run build` completes successfully.
- Status: PASS
- Evidence: Vite production build executed on 30 October 2026.

## 5. Calculation verification

The core associated-loss calculation is:

`Associated loss = sum(abs(realised_pnl)) for matched trades where realised_pnl < 0`

Profitable and zero-P&L matched trades contribute INR 0 and do not offset losses. Rule totals are independent and may overlap across rules.

The planted fixture independently verifies:

- BR-01: 32 matched losing trades, INR 27,650.
- BR-02: 3 matched follow-up trades, INR 18,000.
- BR-03: 2 matched oversized losing trades, INR 14,000.
- BR-04: 2 matched near-expiry losing trades, INR 9,000.

## 6. Bugs and corrections

### BUG-001 Evaluation fixture initially used incorrect boundary inputs

- Related tests: EVAL-005 and EVAL-007.
- Root cause: The first test fixture calls did not express the intended entry minute and one BR-02 follow-up set had profitable rather than losing P&L.
- Fix: Corrected the test fixture generator to support explicit entry minutes and negative follow-up P&L.
- Files: `scripts/run_evals.mjs`.
- Retest: EVAL-005 and EVAL-007 passed; final suite is 10/10.

### Known implementation gaps

These are not claimed as fixed in this evaluation:

- CSV upload checks file type, parseability and required headers, but does not yet provide the full preview, accepted/rejected counts and row-level reasons required by the specification.
- The current UI displays a neutral improvement suggestion but does not yet implement a dedicated select-and-confirm completion screen.
- Loading and duplicate-ID validation are not yet exposed as complete user-facing states.

## 7. Overall evaluation summary

| Result | Count |
|---|---:|
| Total executed automated cases | 10 |
| Passed | 10 |
| Failed | 0 |
| Blocked | 0 |
| Not run | 0 |
| Pass percentage | 100% |

The 100% pass percentage applies to the ten executed deterministic and build cases. It does not mean every specification item is implemented; the known UI gaps above remain open.

## 8. Final ship decision

### READY WITH KNOWN LIMITATIONS

TradeMirror meets the critical calculation, ranking, planted-fixture, clean-data and safety quality bars for the narrow demo MVP. The core financial calculations are deterministic and independently verified, and the Behaviour Timeline reuses the same rule evidence.

It is not yet ready to claim full specification completeness because CSV validation/reconciliation, loading states, duplicate-ID handling and the dedicated improvement-selection completion flow remain incomplete.

## 9. Recommended next improvements

1. Add a CSV preview step showing total, accepted and rejected rows with row-level reasons before analysis.
2. Add duplicate-ID, timezone and numeric-field validation without silently dropping records.
3. Add the improvement-selection and completion screen specified in SCR-05.
4. Add browser-level automated tests for mobile layout, keyboard navigation and CSV error states.
