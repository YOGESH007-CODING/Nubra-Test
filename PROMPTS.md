# TradeMirror Prompt Log

This document records the prompts used by the product owner while building TradeMirror. It includes useful prompts as written and lightly improved versions of vague prompts. The improvements preserve the original intent; they are not new requirements.

This log includes user prompts and user-provided source prompts only. It does not include internal assistant tool instructions.

## Prompt 01 Select the case and create the one-pager

### Original prompt used

> based on this first generate the one pager

### Improved reusable prompt

> Using the attached Nubra assignment, reference guide and product notes, create a 300–700 word one-pager for Case 03 Post-Trade Review. Use TradeMirror as the proposed product. Cover the problem statement, why Nubra should solve it, scope, out of scope, solution space, how it will be tested and next steps. Do not claim that tests were run unless results are provided.

### Result

Created `output/pdf/Nubra_TradeMirror_OnePager.pdf`.

## Prompt 02 Add the SEBI source and latest figures

### Original prompt used

> add latest numbers from sebi and site that only

### Improved reusable prompt

> Update the one-pager using the latest official SEBI source available on sebi.gov.in. Add the current individual-trader loss percentage, aggregate loss amount and options-loss share if reported. Link to the specific SEBI study, not only the homepage. Preserve the distinction between SEBI’s individual-trader category and retail traders, and do not use third-party sources.

### Result

The one-pager was updated with SEBI FY25–FY26 figures and a direct link to the official study.

## Prompt 03 Build the product project

### Original prompt used

> create project based on the above document

### Improved reusable prompt

> Build the TradeMirror MVP from the attached product specification. Use a client-side React + Vite app. Implement CSV upload, preloaded demo data, deterministic detection of the four specified behaviours, ranked top-three insights, expandable evidence, one neutral improvement prompt, safety disclosures and clean no-pattern states. Keep broker integration, tax reporting, prediction, buy/sell advice and chart-heavy dashboards out of scope. Run a production build and verify the main flow in a browser.

### Result

Created the React + Vite project with the main analysis and review flow.

## Prompt 04 Generate and seed the datasets

### Original prompt used

> and all these datasets ... also one more thing pre seed them in the frontend in self so that they can just add those demo

### Improved reusable prompt

> Generate the synthetic TradeMirror datasets described in the attached generator prompt. Include a planted-habits CSV, an expected-results CSV and a validation report. Add a clean control CSV with losses but no qualifying habits. Seed both datasets directly into the frontend so reviewers can select a demo without uploading a file. Verify that the planted fixture detects all four rules and that the clean fixture produces no fabricated insights.

### Result

Added planted and clean CSV fixtures, expected results, validation output and frontend-generated fixtures.

## Prompt 05 Add the Behaviour Timeline

### Original prompt used

> make changes based on this

### Improved reusable prompt

> Update the TradeMirror app using the attached specification’s Behaviour Timeline enhancement. Keep the existing deterministic rules unchanged. Add a secondary date-based timeline below the ranked insights. Reuse existing matched trade IDs and evidence. Support date selection, event details, cluster counts, accessible rule labels, BR-02 prior-loss and elapsed-time context, evidence drill-down and clear empty states. Keep it readable on mobile and do not turn it into a P&L dashboard.

### Result

Added the `BehaviourTimeline` component and connected it to the existing rule results.

## Prompt 06 Clarify the detection algorithm

### Original prompt used

> what's the ml algo or what are we using to find out the bad habits

### Improved reusable prompt

> Explain whether TradeMirror uses ML, an LLM or deterministic rules to identify bad trading habits. Describe each detection rule, its threshold, how associated losses are calculated and why that approach is appropriate for the MVP.

### Result

Documented that the MVP uses deterministic, auditable rule-based analysis rather than ML or an LLM for financial calculations.

## Prompt 07 Document all project prompts

### Original prompt used

> document all the pormpt as referecnes given by me in the proejct and give me that

### Improved reusable prompt

> Create a project-level prompt log containing only the prompts I used while building TradeMirror. Preserve strong prompts as written. For vague or poorly worded prompts, improve them lightly without changing their intent. Include the original prompt, improved reusable prompt, source context and resulting project change. Exclude internal assistant instructions.

### Result

Created this `PROMPTS.md` file.

## Source prompts supplied with the project

The following user-provided files were used as references for the prompts above:

- [Nubra.pdf](/Users/yogeshsharma/Documents/Nubra.pdf)
- [Nubra Product Assignment.pdf](/Users/yogeshsharma/Downloads/Nubra%20Product%20Assignment.pdf)
- [TradeMirror_Product_Specification.docx](/Users/yogeshsharma/Downloads/TradeMirror_Product_Specification.docx)
- [TradeMirror_Product_Specification_with_Behaviour_Timeline.docx](/Users/yogeshsharma/Downloads/TradeMirror_Product_Specification_with_Behaviour_Timeline.docx)
- [Original product notes](/Users/yogeshsharma/.codex/attachments/5b7d1372-4e35-4709-ae39-2c626105da43/Pasted%20text.txt)
- [Case guidance](/Users/yogeshsharma/.codex/attachments/44e62c2a-4289-490c-978d-eb39d9fd4f29/Pasted%20text.txt)
- [Synthetic dataset generator prompt](/Users/yogeshsharma/.codex/attachments/94145e8a-e35c-45ce-b5ae-25fad8003cf9/Pasted%20text.txt)

## Prompt quality notes

- Strong prompts specify the source, requested output, scope, constraints and verification bar.
- The improved versions clarify the desired result without adding unrelated features.
- Financial calculations remain deterministic and auditable.
- No prompt in this log authorises broker access, live trading, user-data transmission or investment advice.
