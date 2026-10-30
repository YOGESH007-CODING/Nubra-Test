from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

OUT = "/Users/yogeshsharma/Desktop/Projects/NUBRA/output/pdf/Nubra_TradeMirror_OnePager.pdf"
navy = colors.HexColor("#102A43")
blue = colors.HexColor("#1F6FEB")
ink = colors.HexColor("#243B53")
muted = colors.HexColor("#52606D")
line = colors.HexColor("#D9E2EC")
soft = colors.HexColor("#F0F4F8")
styles = getSampleStyleSheet()
title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=navy, spaceAfter=4)
subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, leading=14, textColor=muted, spaceAfter=10)
section = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=blue, spaceBefore=7, spaceAfter=3)
body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=12.4, textColor=ink, spaceAfter=3)
small = ParagraphStyle("Small", parent=body, fontSize=8.4, leading=11.2, textColor=muted)
reference = ParagraphStyle("Reference", parent=body, fontSize=7.8, leading=10, textColor=muted, spaceBefore=5)
metric = ParagraphStyle("Metric", parent=body, fontName="Helvetica-Bold", fontSize=9, leading=11.5, textColor=navy)

def P(text, style=body):
    return Paragraph(text, style)

doc = SimpleDocTemplate(OUT, pagesize=letter, rightMargin=0.58*inch, leftMargin=0.58*inch, topMargin=0.48*inch, bottomMargin=0.45*inch, title="Nubra TradeMirror One Pager", author="OpenAI")
story = [P("TradeMirror", title), P("Post-Trade Review for Retail Traders | Nubra Product Assignment - Case 03", subtitle)]

summary = Table([[P("RECOMMENDATION", metric), P("Build a focused review tool that turns one month of completed trades into the two or three behavioural patterns most associated with losses.", body)]], colWidths=[1.55*inch, 5.58*inch])
summary.setStyle(TableStyle([("BACKGROUND", (0,0), (0,0), soft), ("BOX", (0,0), (-1,-1), 0.6, line), ("INNERGRID", (0,0), (-1,-1), 0.4, line), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
story += [summary, Spacer(1, 4)]

story += [P("Problem statement", section), P("A retail trader who trades regularly struggles to understand why losses repeat because a monthly order history shows what happened, not the behavioural patterns behind it. This matters because the trader keeps checking P&amp;L without getting a practical change to make next month.")]
story += [P("Why Nubra should solve it", section), P("SEBI's latest study of the Equity Derivatives Segment reports that 87.7% of individual traders incurred losses in FY26, with aggregate net losses of INR 91,685 crore; options accounted for 92% of aggregate individual losses. SEBI's individual-trader category includes resident individuals, HUFs, NRIs, sole proprietorships and individual investors under portfolio managers, so this is a strong signal of the risk faced by retail-like participants. TradeMirror supports Nubra's mission of giving retail traders the clarity professionals already have: it makes recurring behaviour and financial impact explainable, creates a reason to return after a trading month, and differentiates Nubra through behavioural insight rather than another performance dashboard. Nubra is well placed because it already sits close to the trader's order history and can start with a sample CSV, without broker integration.")]

story += [P("Scope", section)]
scope_data = [[P("In scope", metric), P("Out of scope", metric)], [P("• Upload CSV or use preloaded demo data<br/>• Detect 4 rules: holding losers too long; post-loss follow-up trading; oversized positions; trades close to expiry<br/>• Rank only the top 2-3 patterns by associated rupee loss<br/>• Show evidence, trade count, and one practical, non-judgmental improvement", small), P("• Live broker integration - not needed to validate the core insight<br/>• Tax reports and full analytics - distract from the review job<br/>• Future-trade prediction or buy/sell advice - unsafe and outside the brief<br/>• A dashboard of charts - the user needs a short review, not more noise", small)]]
scope = Table(scope_data, colWidths=[3.55*inch, 3.58*inch])
scope.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), soft), ("BOX", (0,0), (-1,-1), 0.6, line), ("INNERGRID", (0,0), (-1,-1), 0.4, line), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
story += [scope]

story += [P("Solution space", section), P("I considered three approaches: a chart-heavy analytics dashboard, a searchable trade ledger, and a ranked behavioural review. I would build the third. It best matches the brief because it compresses a month of data into a one-minute explanation: <b>what am I repeatedly doing, how much money was associated with it, and what should I monitor next?</b>")]
story += [P("The core flow is: upload or open demo data -> analyse completed trades -> show the top patterns -> expand evidence -> choose one improvement to carry into the next month. The language should describe observable sequences, not diagnose intent: \"trades opened within 30 minutes of a loss\" is safer and more useful than \"revenge trading.\" The product should also distinguish association from causation: losses occurred on trades matching the rule; the tool cannot claim the loss would have been avoided.")]
story += [P("How I would test it", section), P("Ship bar: 100% of rupee calculations match manual checks; the demo dataset surfaces all planted habits and ranks the correct top three; clean data does not invent a problem; and a non-trader can explain each insight's evidence and suggested improvement. I would also test empty files, too few trades, tied patterns, and missing holding-time fields before shipping. The app should remain a review tool, display \"For demo purposes only. Not investment advice,\" and never hide or understate risk.")]
story += [P("What I would do next", section), P("1. Validate the first review with one or two regular traders and observe where evidence is misunderstood. 2. Add a month-over-month comparison so users can see whether a behaviour is changing. 3. Explore a private, read-only broker connection only after the CSV workflow proves the insight is valuable.")]
story += [P("Source: SEBI, <link href='https://www.sebi.gov.in/reports-and-statistics/research/aug-2026/study-profitability-of-individual-traders-in-the-equity-derivatives-segment-fy25-fy26-_103835.html' color='#1F6FEB'>Study - Profitability of Individual Traders in the Equity Derivatives Segment (FY25-FY26)</link>, published 20 August 2026.", reference)]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(line)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 0.31*inch, letter[0]-doc.rightMargin, 0.31*inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(muted)
    canvas.drawString(doc.leftMargin, 0.17*inch, "TradeMirror | Illustrative product concept")
    canvas.drawRightString(letter[0]-doc.rightMargin, 0.17*inch, "1")
    canvas.restoreState()

doc.build(story, onFirstPage=footer)
print(OUT)
