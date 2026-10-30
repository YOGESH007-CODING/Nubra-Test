# TradeMirror

TradeMirror is a client-side post-trade review MVP for the Nubra Case 03 assignment.

## Run

```bash
npm install
npm run dev
```

## Demo datasets

The start screen includes two self-contained fixtures:

- **Planted habits**: 100 synthetic trades that exercise the four behavioural rules.
- **Clean controls**: 100 synthetic trades with ordinary losses but no qualifying pattern.

The downloadable CSV fixtures live in `public/datasets/`:

- `trademirror_planted_habits.csv`
- `trademirror_planted_habits_expected_results.csv`
- `trademirror_planted_habits_validation.txt`
- `trademirror_clean_controls.csv`

The frontend copy is generated into `src/data/generatedFixtures.js` so the demos work without a network request or file upload.

The generated figures are synthetic and for product testing only. Rule thresholds are provisional defaults from the product specification, not trading advice.
