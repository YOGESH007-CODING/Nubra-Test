from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT = Path('/Users/yogeshsharma/Desktop/Projects/NUBRA/output/docs/TradeMirror_Evals_Artifact03.docx')
OUT.parent.mkdir(parents=True, exist_ok=True)
NAVY='132238'; BLUE='1F6FEB'; LIGHT='EEF3F7'; BORDER='D9E2EC'; GREEN='13795B'; GRAY='667386'

def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=tcPr.find(qn('w:shd'))
    if shd is None: shd=OxmlElement('w:shd'); tcPr.append(shd)
    shd.set(qn('w:fill'), fill)

def borders(table):
    tblPr=table._tbl.tblPr; border=tblPr.first_child_found_in('w:tblBorders')
    if border is None: border=OxmlElement('w:tblBorders'); tblPr.append(border)
    for edge in ('top','left','bottom','right','insideH','insideV'):
        tag='w:'+edge; el=border.find(qn(tag))
        if el is None: el=OxmlElement(tag); border.append(el)
        el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'4'); el.set(qn('w:color'),BORDER)

def cell_text(cell, text, bold=False, color='243B53', size=8.2):
    cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(0)
    r=p.add_run(str(text)); r.bold=bold; r.font.size=Pt(size); r.font.color.rgb=RGBColor.from_string(color)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    tc=cell._tc.get_or_add_tcPr(); mar=tc.first_child_found_in('w:tcMar')
    if mar is None: mar=OxmlElement('w:tcMar'); tc.append(mar)
    for side in ('top','bottom','left','right'):
        node=mar.find(qn('w:'+side))
        if node is None: node=OxmlElement('w:'+side); mar.append(node)
        node.set(qn('w:w'),'80'); node.set(qn('w:type'),'dxa')

def heading(doc, text, level=1):
    p=doc.add_paragraph(style=f'Heading {level}'); p.paragraph_format.space_before=Pt(11); p.paragraph_format.space_after=Pt(4)
    r=p.add_run(text); r.font.color.rgb=RGBColor.from_string(NAVY if level==1 else BLUE); return p

def body(doc, text):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(4); p.paragraph_format.line_spacing=1.08; p.add_run(text); return p

def bullet(doc, text):
    p=doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after=Pt(1); p.paragraph_format.left_indent=Inches(.2); p.add_run(text)

doc=Document(); sec=doc.sections[0]; sec.top_margin=Inches(.55); sec.bottom_margin=Inches(.55); sec.left_margin=Inches(.62); sec.right_margin=Inches(.62)
doc.styles['Normal'].font.name='Aptos'; doc.styles['Normal'].font.size=Pt(9.5); doc.styles['Normal'].font.color.rgb=RGBColor.from_string('243B53')
for name,size in [('Heading 1',15),('Heading 2',11.5)]:
    doc.styles[name].font.name='Aptos Display'; doc.styles[name].font.size=Pt(size); doc.styles[name].font.bold=True; doc.styles[name].font.color.rgb=RGBColor.from_string(NAVY if name=='Heading 1' else BLUE)
header=sec.header.paragraphs[0]; header.text='TRADEMIRROR  /  ARTIFACT 03'; header.alignment=WD_ALIGN_PARAGRAPH.RIGHT; header.runs[0].font.size=Pt(8); header.runs[0].font.bold=True; header.runs[0].font.color.rgb=RGBColor.from_string(GRAY)
footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER; footer.add_run('TradeMirror · Evaluation document · 30 October 2026').font.size=Pt(8)

p=doc.add_paragraph(); r=p.add_run('TradeMirror'); r.bold=True; r.font.size=Pt(25); r.font.color.rgb=RGBColor.from_string(NAVY)
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(9); r=p.add_run('Artifact 03  |  Product Evaluation and Evals'); r.font.size=Pt(11); r.font.color.rgb=RGBColor.from_string(GRAY)

intro=doc.add_table(rows=1, cols=2); intro.alignment=WD_TABLE_ALIGNMENT.CENTER; intro.autofit=False; intro.columns[0].width=Inches(1.45); intro.columns[1].width=Inches(5.8)
cell_text(intro.cell(0,0),'SHIP BAR',True,NAVY,9); shade(intro.cell(0,0),LIGHT); cell_text(intro.cell(0,1),'100% calculation correctness, all planted rules detected, no clean-data false positives, and zero unsupported advice or causal claims.',False,'243B53',9); borders(intro)

heading(doc,'Evaluation overview'); body(doc,'TradeMirror is a client-side post-trade review tool for retail traders. This evaluation tests whether it turns completed trade records into explainable behavioural insights without inventing problems or giving trading advice.'); body(doc,'The evaluation covers correctness, clarity, edge cases, data quality, safety and the main user workflow. It uses the 100-trade planted-habits fixture, the 100-trade clean-control fixture, direct rule-engine tests and browser verification of the demo and Behaviour Timeline.')
heading(doc,'What was tested')
for x in ['Correctness: independent calculations for all four behavioural rules.','Clarity: insight title, matched-trade count, associated loss and improvement wording.','Edge cases: exact thresholds, outside-window values, insufficient evidence and overlapping rules.','Safety and honesty: no fabricated patterns, no buy/sell recommendations and association-not-causation wording.','Functional flow: select demo, review ranked insights, expand evidence, select a timeline date and open linked evidence.']: bullet(doc,x)
heading(doc,'Test strategy and environment'); body(doc,'The deterministic analysis was executed with scripts/run_evals.mjs using Node.js. Expected numbers were calculated independently and compared against the generated expected-results file. npm run build was executed for production-build verification. Browser checks were performed against the local Vite app using the planted and clean demos.'); body(doc,'No broker connection, live prices, backend, AI model or real customer data was used. The test fixtures are synthetic INR trades.')

heading(doc,'Ship bar')
ship=doc.add_table(rows=1,cols=3); ship.alignment=WD_TABLE_ALIGNMENT.CENTER; ship.autofit=False
for i,w in enumerate([1.65,2.9,2.7]): ship.columns[i].width=Inches(w)
for i,h in enumerate(['Dimension','Pass criterion','Why it matters']): cell_text(ship.cell(0,i),h,True,'FFFFFF',8.5); shade(ship.cell(0,i),NAVY)
for row in [('Financial calculations','100% correct','One wrong rupee value breaks trust.'),('Core detection','All planted rules detected','The product promise depends on repeatable detection.'),('Clean data','No fabricated insights','Silence is safer than invented behaviour.'),('Ranking','Correct descending order','Users see the most relevant patterns first.'),('Safety and honesty','Zero advice or causal claims','The product informs; it does not direct trades.')]:
    cells=ship.add_row().cells
    for i,v in enumerate(row): cell_text(cells[i],v,False,'243B53',8.2)
borders(ship)

heading(doc,'Evaluation results'); body(doc,'The executed suite contains ten independent cases. All ten passed after the boundary fixtures were corrected. The pass percentage is 10/10 for the executed automated cases; it does not claim full specification completeness.')
tests=[('EVAL-001','Correctness','Planted fixture detection','100 synthetic trades','All four detected; visible top three BR-01, BR-02, BR-03.','All four detected; top three matched.','PASS'),('EVAL-002','Correctness','Associated-loss totals','Planted fixture','BR-01 27,650; BR-02 18,000; BR-03 14,000; BR-04 9,000.','Exact totals matched CSV.','PASS'),('EVAL-003','Safety','Clean controls','100 clean trades','Zero eligible patterns.','Zero insights; neutral state.','PASS'),('EVAL-004','Correctness','BR-01 exact 2x boundary','Win median 50m; loss median 100m.','Qualifies; 3 matches; INR 900.','Qualifies; INR 900.','PASS'),('EVAL-005','Correctness','BR-02 30m boundary','Two at 30m; one at 31m.','Two matches; INR 400 loss.','Two matches; INR 400.','PASS'),('EVAL-006','Correctness','BR-03 threshold','Baseline INR 1,000; 2 losing >=2x; 1 profitable oversized.','Only losing oversized positions.','Two included; profitable excluded.','PASS'),('EVAL-007','Correctness','BR-04 24h boundary','Two at 24h; one at 24h 1m.','Two matches; one excluded.','Two matches; one excluded.','PASS'),('EVAL-008','Correctness','Overlapping matches','TM-097 and TM-098.','Independent totals; no combined loss.','Overlap preserved; Net P&L INR -33,050.','PASS'),('EVAL-009','Data quality','Invalid-row containment','One valid; one invalid timestamp.','Invalid row cannot create a loss.','Invalid row excluded; valid result retained.','PASS'),('EVAL-010','Functional','Production build','npm run build','Build completes.','Build completed.','PASS')]
t=doc.add_table(rows=1,cols=7); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
for i,w in enumerate([.62,.85,1.15,1.2,1.55,1.45,.7]): t.columns[i].width=Inches(w)
for i,h in enumerate(['ID','Type','Objective','Input','Expected','Actual','Status']): cell_text(t.cell(0,i),h,True,'FFFFFF',7.7); shade(t.cell(0,i),NAVY)
for row in tests:
    cells=t.add_row().cells
    for i,v in enumerate(row): cell_text(cells[i],v,False,GREEN if i==6 else '243B53',7.1)
    shade(cells[6],'E6F4F1')
borders(t)

heading(doc,'Independent calculation verification'); body(doc,'Associated loss = sum(abs(realised_pnl)) for matched trades where realised_pnl < 0. Profitable and zero-P&L matched trades do not offset losses. Rule totals are independent and may overlap across rules.')
calc=doc.add_table(rows=1,cols=4); calc.alignment=WD_TABLE_ALIGNMENT.CENTER; calc.autofit=False
for i,w in enumerate([1,2.2,1.4,2.4]): calc.columns[i].width=Inches(w)
for i,h in enumerate(['Rule','Independent check','Expected','Observed']): cell_text(calc.cell(0,i),h,True,'FFFFFF',8); shade(calc.cell(0,i),NAVY)
for row in [('BR-01','32 matched losing trades','INR 27,650','INR 27,650'),('BR-02','3 follow-up trades','INR 18,000','INR 18,000'),('BR-03','2 oversized losing trades','INR 14,000','INR 14,000'),('BR-04','2 near-expiry losing trades','INR 9,000','INR 9,000')]:
    cells=calc.add_row().cells
    for i,v in enumerate(row): cell_text(cells[i],v,False,'243B53',8)
borders(calc)

heading(doc,'Bugs, fixes and known limitations'); body(doc,'BUG-001 — Evaluation fixture boundary setup. The first BR-02 and BR-04 test inputs did not express the intended minute-level boundaries. The fixture helper was corrected to support explicit entry minutes and negative follow-up P&L. The affected tests were rerun and passed.'); body(doc,'Known implementation gaps: CSV upload checks file type, parseability and required headers but does not yet expose the full preview, accepted/rejected counts and row-level reasons required by the broader specification. The UI shows a neutral improvement suggestion but does not yet implement a dedicated select-and-confirm completion screen. Loading, duplicate-ID and timezone validation are not yet complete user-facing states.')
heading(doc,'Overall result and ship decision')
summary=doc.add_table(rows=1,cols=2); summary.alignment=WD_TABLE_ALIGNMENT.CENTER; summary.autofit=False; summary.columns[0].width=Inches(2.6); summary.columns[1].width=Inches(4.4)
for i,h in enumerate(['Metric','Result']): cell_text(summary.cell(0,i),h,True,'FFFFFF',8.5); shade(summary.cell(0,i),NAVY)
for row in [('Executed cases','10'),('Passed','10'),('Failed / blocked / not run','0 / 0 / 0'),('Pass percentage','100% of executed automated cases'),('Final decision','READY WITH KNOWN LIMITATIONS')]:
    cells=summary.add_row().cells; cell_text(cells[0],row[0],row[0]=='Final decision',NAVY,8.2); cell_text(cells[1],row[1],row[0]=='Final decision',GREEN if row[0]=='Final decision' else '243B53',8.2)
borders(summary); body(doc,'The calculation and safety bars for the narrow demo MVP are met. The product is not presented as fully specification-complete until CSV reconciliation, loading and duplicate-ID states, and the improvement-selection completion flow are implemented.')

doc.core_properties.title='TradeMirror Evaluation Artifact 03'; doc.core_properties.subject='Product evaluation and evals'; doc.core_properties.author='TradeMirror Product Team'; doc.save(OUT); print(OUT)
