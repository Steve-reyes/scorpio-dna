"""PDF report generation"""
import io
from weasyprint import HTML

REPORT_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 11px; color: #1D1D1F; margin: 40px; }
  h1 { font-size: 24px; margin-bottom: 5px; }
  h2 { font-size: 18px; color: #5856D6; border-bottom: 2px solid #5856D6; padding-bottom: 5px; margin-top: 30px; }
  h3 { font-size: 14px; margin: 15px 0 5px; }
  .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #E5E5EA; }
  .disclaimer { background: #FFF2F0; border: 1px solid #FF3B30; padding: 10px 15px; border-radius: 6px; font-size: 10px; color: #666; margin: 20px 0; }
  .disclaimer strong { color: #FF3B30; }
  .card { border: 1px solid #E5E5EA; border-radius: 8px; padding: 10px 15px; margin: 8px 0; page-break-inside: avoid; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 600; color: white; }
  .badge.high { background: #FF3B30; }
  .badge.elevated { background: #FF9500; }
  .badge.typical { background: #34C759; }
  .badge.carrier { background: #007AFF; }
  .meta { color: #86868B; font-size: 10px; margin-top: 5px; }
  .summary-grid { display: flex; gap: 15px; flex-wrap: wrap; margin: 15px 0; }
  .summary-item { background: #F5F5F7; border-radius: 8px; padding: 10px 15px; flex: 1; min-width: 120px; text-align: center; }
  .summary-item .num { font-size: 24px; font-weight: 700; }
  .summary-item .label { font-size: 10px; color: #86868B; }
  .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E5EA; font-size: 9px; color: #86868B; text-align: center; }
</style>
</head>
<body>
<div class="header">
  <h1>🦂 Scorpio DNA Report</h1>
  <p style="color:#86868B;font-size:12px">Generated {date} &middot; {total} conditions matched</p>
</div>

<div class="disclaimer">
  <strong>⚠ For Educational Purposes Only</strong> — this report is not medical advice, not FDA-approved, not diagnostic.
  Consult a healthcare professional before making health decisions based on this data.
</div>

<div class="summary-grid">
  <div class="summary-item"><div class="num">{total}</div><div class="label">Conditions Analyzed</div></div>
  <div class="summary-item"><div class="num">{high}</div><div class="label">Higher Risk</div></div>
  <div class="summary-item"><div class="num">{elevated}</div><div class="label">Elevated</div></div>
  <div class="summary-item"><div class="num">{carrier}</div><div class="label">Carrier</div></div>
</div>

{categories_html}

<div class="footer">
  Scorpio DNA — Raw DNA Analysis Tool &middot; {date}
</div>
</body>
</html>"""

CATEGORY_HTML = """
<h2>{cat_icon} {category}</h2>
<p style="color:#86868B;font-size:11px;margin:2px 0">{count} conditions</p>
{cards_html}
"""

CARD_HTML = """
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h3 style="margin:0">{trait}</h3>
    <span class="badge {result}">{status_text}</span>
  </div>
  <p style="margin:5px 0;font-size:11px;color:#666">{description[:200]}{'...' if len(description)>200 else ''}</p>
  <div class="meta">Genotype: {genotype} &middot; Risk Allele: {risk_allele} &middot; Population Freq: {pop:.0%} &middot; rsID: {rsid}</div>
  {study_link}
</div>
"""

CATEGORY_ICONS = {
    "Health": "🩺",
    "Carrier": "🧬",
    "Drug Response": "💊",
    "Traits": "🧠",
    "Nutrition": "🥗",
    "Fitness": "🏃",
    "Personality": "🎭",
}

def generate_pdf_report(summary: dict) -> bytes:
    total = summary["total_matched"]
    results = summary["results"]
    categories = summary["categories"]

    high_count = sum(1 for r in results if r["result"] == "high")
    elevated_count = sum(1 for r in results if r["result"] == "elevated")
    carrier_count = sum(1 for r in results if r["result"] == "carrier")

    # Group results by category
    from collections import defaultdict
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)

    # Order categories
    cat_order = ["Health", "Carrier", "Drug Response", "Traits", "Nutrition", "Fitness", "Personality"]
    categories_html = ""
    for cat in cat_order:
        if cat not in by_cat:
            continue
        cards = by_cat[cat]
        cards_html = ""
        for r in cards:
            study = f'<a href="{r["study_url"]}" style="font-size:10px;color:#5856D6">View Study</a>' if r["study_url"] else ""
            cards_html += CARD_HTML.format(
                trait=r["trait"],
                status_text=r["status_text"],
                result=r["result"],
                description=r["description"],
                genotype=r["genotype"],
                risk_allele=r["risk_allele"],
                pop=r["population_freq"],
                rsid=r["rsid"],
                study_link=study,
            )
        categories_html += CATEGORY_HTML.format(
            cat_icon=CATEGORY_ICONS.get(cat, "📋"),
            category=cat,
            count=len(cards),
            cards_html=cards_html,
        )

    from datetime import datetime
    now = datetime.now().strftime("%B %d, %Y")

    html = REPORT_HTML.format(
        date=now,
        total=total,
        high=high_count,
        elevated=elevated_count,
        carrier=carrier_count,
        categories_html=categories_html,
    )

    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
