"""Build 'Data Science Capstone Project Report' slides (PDF, 16:9).
Chạy sau khi đã chạy 01-08: các ảnh viz_*.png, cm_*.png, model_comparison.png trong thư mục này
sẽ được chèn tự động. Ảnh nào chưa có thì hiện khung placeholder (chụp screenshot rồi chạy lại).
Usage: python build_report.py [output.pdf]
"""
import os
import sys
from reportlab.lib.pagesizes import landscape
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfgen import canvas

W, H = 960, 540
NAVY, BLUE, LIGHT, GREY, ORANGE = HexColor("#0B2545"), HexColor("#1F6FB2"), HexColor("#EAF2FA"), HexColor("#6B7785"), HexColor("#D35400")
GITHUB = "https://github.com/hongan151206-ai/Capstone-project"
OUT = sys.argv[1] if len(sys.argv) > 1 else "Data_Science_Capstone_Project_Report.pdf"
c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("Data Science Capstone Project Report")
page = [0]


def new_slide(title, github=True):
    if page[0]:
        c.showPage()
    page[0] += 1
    c.setFillColor(white); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(NAVY); c.rect(0, H - 70, W, 70, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 26); c.drawString(36, H - 45, title)
    c.setFillColor(GREY); c.setFont("Helvetica", 10)
    c.drawRightString(W - 30, 14, f"{page[0]}")
    if github:
        c.setFillColor(BLUE); c.setFont("Helvetica", 10)
        c.drawString(36, 14, f"GitHub: {GITHUB}")
        c.linkURL(GITHUB, (36, 8, 400, 26), relative=0)


def text(x, y, s, size=15, font="Helvetica", color=black, width=None, lead=None):
    c.setFillColor(color); c.setFont(font, size)
    lines = simpleSplit(s, font, size, width) if width else [s]
    lead = lead or size * 1.3
    for ln in lines:
        c.drawString(x, y, ln); y -= lead
    return y


def bullets(items, x=40, y=H - 110, width=W - 80, size=16, gap=8):
    for it in items:
        sub = it.startswith("- ")
        s = it[2:] if sub else it
        xx = x + (24 if sub else 0)
        fs = size - (2 if sub else 0)
        c.setFillColor(BLUE if not sub else GREY); c.circle(xx + 4, y + fs * 0.32, 2.6, fill=1, stroke=0)
        y = text(xx + 16, y, s, fs, width=width - (xx - x) - 16)
        y -= gap
    return y


def box(x, y, w, h, s, fill=LIGHT, size=12, bold=False):
    c.setFillColor(fill); c.setStrokeColor(BLUE); c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setFillColor(NAVY); f = "Helvetica-Bold" if bold else "Helvetica"
    lines = simpleSplit(s, f, size, w - 12)
    ty = y + h / 2 + (len(lines) - 1) * size * 0.6 - size * 0.3
    c.setFont(f, size)
    for ln in lines:
        c.drawCentredString(x + w / 2, ty, ln); ty -= size * 1.2


def arrow(x1, y1, x2, y2):
    c.setStrokeColor(GREY); c.setFillColor(GREY); c.setLineWidth(1.5); c.line(x1, y1, x2, y2)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    p = c.beginPath(); p.moveTo(x2, y2)
    p.lineTo(x2 - 9 * math.cos(a - 0.4), y2 - 9 * math.sin(a - 0.4))
    p.lineTo(x2 - 9 * math.cos(a + 0.4), y2 - 9 * math.sin(a + 0.4)); p.close(); c.drawPath(p, fill=1, stroke=0)


def flow(steps, y, x0=36, bw=140, bh=62, gap=26, size=11):
    x = x0
    for i, s in enumerate(steps):
        box(x, y, bw, bh, s, size=size)
        if i < len(steps) - 1:
            arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2)
        x += bw + gap


def picture(fname, x, y, w, h, label):
    if os.path.exists(fname):
        img = ImageReader(fname); iw, ih = img.getSize(); r = min(w / iw, h / ih)
        c.drawImage(img, x + (w - iw * r) / 2, y + (h - ih * r) / 2, iw * r, ih * r)
    else:
        c.setStrokeColor(GREY); c.setDash(4, 3); c.rect(x, y, w, h, fill=0, stroke=1); c.setDash()
        c.setFillColor(GREY); c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(x + w / 2, y + h / 2 + 6, "[Insert chart / screenshot]")
        c.drawCentredString(x + w / 2, y + h / 2 - 10, label)


def caption(s):
    text(40, 52, s, 13, "Helvetica-Oblique", NAVY, width=W - 80)


# 1 ---------------------------------------------------------------- Title
new_slide("Data Science Capstone Project Report", github=True)
text(40, H - 140, "Predicting SpaceX Falcon 9 First-Stage Landing Success", 28, "Helvetica-Bold", NAVY, width=W - 80)
text(40, H - 230, "IBM Applied Data Science Capstone", 18, color=GREY)
text(40, H - 262, "Author: Hong An Vo", 18, color=GREY)
text(40, H - 294, f"Project repository: {GITHUB}", 14, color=BLUE)

# 2 ---------------------------------------------------------------- Executive Summary (1.3)
new_slide("Executive Summary")
bullets([
    "Problem: SpaceX advertises Falcon 9 launches at ~$62M vs $165M+ for competitors, because the first stage is reused. "
    "Predicting whether the first stage lands lets us estimate launch cost.",
    "Methods: data collected via SpaceX REST API and Wikipedia web scraping; cleaned and labelled with pandas "
    "(Class = 1 if landing succeeded); explored with SQL and Matplotlib/Seaborn; mapped with Folium; "
    "dashboard built with Plotly Dash; four classifiers tuned with GridSearchCV.",
    "Key results: landing success rate improved steadily over time and with more flights; "
    "success depends on orbit, launch site and payload mass; all four models reach similar test accuracy "
    "(best model: [name], accuracy [XX%]).",
    "Conclusion: landing outcome can be predicted reliably from pre-launch features, giving a basis for "
    "cost estimation by competing bidders.",
], size=15)

# 3 ---------------------------------------------------------------- Introduction (1.4)
new_slide("Introduction")
text(40, H - 105, "Project background", 18, "Helvetica-Bold", BLUE)
y = bullets([
    "Commercial space travel is growing; SpaceX is the most successful company thanks to reusable rockets.",
    "Falcon 9 launch is priced ~$62M; other providers charge upwards of $165M. The saving comes from reusing the first stage.",
], y=H - 135, size=15)
text(40, y - 6, "Problem statement", 18, "Helvetica-Bold", BLUE)
bullets([
    "Act as a data scientist for a company bidding against SpaceX.",
    "Determine the price of each launch by predicting whether the Falcon 9 first stage will land successfully.",
    "Questions: which factors drive landing success? How does success change over time? Which model predicts best?",
], y=y - 36, size=15)

# 4 ---------------------------------------------------------------- Data Collection API (1.5)
new_slide("Data Collection - SpaceX API")
text(40, H - 100, "Flowchart", 16, "Helvetica-Bold", BLUE)
flow(["GET /v4/launches/past", "Normalize JSON (pandas)", "Filter: 1 core, 1 payload, date <= 2020-11-13",
      "Call /rockets, /launchpads, /payloads, /cores", "Build DataFrame, keep Falcon 9"], H - 190, bw=150, gap=22)
bullets([
    "Key phrases: requests.get() -> .json() -> json_normalize()",
    "Helper functions: getBoosterVersion, getLaunchSite, getPayloadData, getCoreData",
    "Missing PayloadMass replaced with the column mean",
    "Output: dataset_part_1.csv (Falcon 9 launches only)",
    "Code: 01_spacex_api_collection.py",
], y=H - 250, size=14, gap=6)

# 5 ---------------------------------------------------------------- Web scraping (1.6)
new_slide("Data Collection - Web Scraping")
text(40, H - 100, "Flowchart", 16, "Helvetica-Bold", BLUE)
flow(["Request Wikipedia page (Falcon 9 launch list)", "BeautifulSoup parse HTML", "Find launch tables (wikitable)",
      "Extract fields row by row", "Save to DataFrame / CSV"], H - 190, bw=150, gap=22)
bullets([
    "Key phrases: requests.get() -> BeautifulSoup() -> find_all('table') -> parse <th>/<td>",
    "Extracted: flight no., launch site, payload, mass, orbit, customer, outcome, booster version, landing, date, time",
    "Helper functions clean date/time, booster version and landing status",
    "Output: spacex_web_scraped.csv",
    "Code: 02_web_scraping.py",
], y=H - 250, size=14, gap=6)

# 6 ---------------------------------------------------------------- Wrangling (1.7)
new_slide("Data Wrangling Methodology")
bullets([
    "Checked missing values (%) and data types for every column.",
    "Counted launches per site, launches per orbit and landing outcome types.",
    "Landing outcomes: True/False + Ocean, RTLS, ASDS; None = no attempt.",
    "Created binary label Class: 0 for bad outcomes (False Ocean, False RTLS, False ASDS, None ASDS, None None), 1 otherwise.",
    "Computed overall success rate = mean(Class).",
    "One-hot encoded Orbit, LaunchSite, LandingPad and Serial; cast all features to float.",
    "Outputs: dataset_part_2.csv (labelled), dataset_part_3.csv (features)",
    "Code: 03_data_wrangling.py",
], size=15)

# 7 ---------------------------------------------------------------- EDA viz summary (1.8)
new_slide("EDA with Data Visualization")
bullets([
    "Scatter (catplot) Flight Number vs Payload Mass - effect of experience and payload on outcome.",
    "Scatter Flight Number vs Launch Site; Payload Mass vs Launch Site - does the site matter?",
    "Scatter Flight Number vs Orbit; Payload Mass vs Orbit - orbit-specific patterns.",
    "Bar chart: success rate per orbit - which orbits are easiest.",
    "Line chart: yearly success-rate trend - improvement over time.",
    "Purpose: find relationships between features and Class before modelling and select features.",
    "Code: 05_eda_visualization.py",
], size=15)

# 8 ---------------------------------------------------------------- EDA SQL summary (1.9)
new_slide("EDA with SQL")
bullets([
    "Loaded Spacex.csv into table SPACEXTBL and ran 10 queries:",
    "- Unique launch sites; 5 records where site starts with 'CCA'",
    "- Total payload for NASA (CRS); average payload for booster F9 v1.1",
    "- First successful ground-pad landing date",
    "- Boosters with drone-ship success and payload between 4000 and 6000 kg",
    "- Count of successful vs failed missions; boosters carrying the maximum payload",
    "- 2015 failed drone-ship landings (month, booster, site)",
    "- Ranking of landing outcomes between 2010-06-04 and 2017-03-20",
    "Code: 04_eda_sql.py",
], size=15, gap=5)

# 9 ---------------------------------------------------------------- Interactive analytics (1.10)
new_slide("Interactive Visual Analytics")
text(40, H - 105, "Folium map (06_folium_map.py)", 17, "Helvetica-Bold", BLUE)
y = bullets([
    "Markers, circles and labels for every launch site.",
    "Marker clusters: green = successful launch, red = failed launch.",
    "Distance lines from a site to coastline, railway, highway and city.",
], y=H - 135, size=14, gap=5)
text(40, y - 6, "Plotly Dash app (07_dash_app.py)", 17, "Helvetica-Bold", BLUE)
bullets([
    "Dropdown selects launch site (or all sites); pie chart shows success counts.",
    "Range slider filters payload; scatter plot shows payload vs outcome by booster version.",
], y=y - 36, size=14, gap=5)
text(40, 36, f"GitHub (Folium + Dash): {GITHUB}", 12, color=BLUE)

# 10 --------------------------------------------------------------- Viz results 1 (1.11)
new_slide("EDA Results - Scatter Plots")
picture("viz_flight_payload.png", 30, 90, 440, 330, "Flight Number vs Payload Mass")
picture("viz_flight_site.png", 490, 90, 440, 330, "Flight Number vs Launch Site")
caption("Insight: success rate rises with flight number; heavier payloads and some sites show different landing patterns.")

# 11 --------------------------------------------------------------- Viz results 2
new_slide("EDA Results - Orbit and Payload")
picture("viz_payload_orbit.png", 30, 90, 440, 330, "Payload Mass vs Orbit")
picture("viz_flight_orbit.png", 490, 90, 440, 330, "Flight Number vs Orbit")
caption("Insight: some orbits (e.g. LEO, ISS) improve with more flights; others have few launches, so rates are less reliable.")

# 12 --------------------------------------------------------------- Viz results 3
new_slide("EDA Results - Success Rate by Orbit and Yearly Trend")
picture("viz_success_by_orbit.png", 30, 90, 440, 330, "Success rate by orbit (bar chart)")
picture("viz_yearly_trend.png", 490, 90, 440, 330, "Yearly success-rate trend (line chart)")
caption("Insight: success rate increased from 2013 onwards and kept improving through 2020.")

# 13 --------------------------------------------------------------- SQL results 1 (1.12)
new_slide("EDA with SQL - Launch Sites, Payloads, Success Rates")
bullets([
    "Launch sites: [paste output of Q1 - 4 unique sites]",
    "Records for sites starting with 'CCA': [paste output of Q2]",
    "Total payload mass for NASA (CRS): [XXXX kg]",
    "Average payload mass for booster F9 v1.1: [XXXX kg]",
    "First successful ground-pad landing: [YYYY-MM-DD]",
    "Drone-ship successes with 4000-6000 kg payload: [list boosters]",
    "Successful vs failed missions: [N] vs [N]",
    "Boosters with max payload: [list boosters]",
], size=15)
text(40, 52, "Replace the brackets with screenshots/values from 04_eda_sql.py output.", 12, "Helvetica-Oblique", GREY)

# 14 --------------------------------------------------------------- SQL results 2
new_slide("EDA with SQL - Rankings and Time Analysis")
bullets([
    "2015 failed drone-ship landings (month, booster, site): [paste Q9 output]",
    "Landing outcomes ranked by count, 2010-06-04 to 2017-03-20: [paste Q10 output]",
    "Time analysis: first ground-pad success date and the 2015 failures show landing technology maturing over time.",
], size=15)
picture("sql_q10.png", 140, 70, 680, 190, "Screenshot of Q10 ranking table")

# 15 --------------------------------------------------------------- Folium 1 (1.13)
new_slide("Folium Map - Launch Sites and Launch Records")
picture("folium_sites.png", 30, 90, 440, 330, "Map with launch-site markers")
picture("folium_clusters.png", 490, 90, 440, 330, "Marker clusters (green=success, red=failure)")
caption("All launch sites are near the coast (Florida and California). KSC LC-39A / other sites can be compared by success markers.")

# 16 --------------------------------------------------------------- Folium 2
new_slide("Folium Map - Proximity Analysis")
picture("folium_proximity.png", 30, 90, 560, 330, "Distance lines to coastline / railway / highway / city")
bullets([
    "Close to coastline: [x.xx km]",
    "Close to railway: [x.xx km]",
    "Close to highway: [x.xx km]",
    "Far from cities: [xx.xx km]",
], x=610, y=H - 130, width=320, size=14)
caption("Sites sit close to coast, rail and highway for transport and safe over-ocean launches, but far from populated areas.")

# 17 --------------------------------------------------------------- Dash 1 (1.14)
new_slide("Plotly Dash - Success Pie Charts")
picture("dash_pie_all.png", 30, 90, 440, 330, "Pie: total successes by site (ALL)")
picture("dash_pie_site.png", 490, 90, 440, 330, "Pie: success vs failure, best site")
caption("Insight: one site contributes the largest share of successful launches; its own success ratio is the highest.")

# 18 --------------------------------------------------------------- Dash 2
new_slide("Plotly Dash - Payload vs Launch Outcome")
picture("dash_scatter_all.png", 30, 90, 440, 330, "Scatter: payload vs outcome (all sites)")
picture("dash_scatter_range.png", 490, 90, 440, 330, "Scatter with payload slider range")
caption("Insight: low-to-mid payload ranges show higher success; booster version category FT/B4/B5 dominate successes.")

# 19 --------------------------------------------------------------- Predictive method + results (1.15)
new_slide("Predictive Analysis - Models and Evaluation")
bullets([
    "Pipeline: StandardScaler -> train_test_split (80/20) -> GridSearchCV (cv=10) -> evaluate on test set.",
    "Models: Logistic Regression, SVM, Decision Tree, KNN.",
], size=14, y=H - 105)
picture("model_comparison.png", 30, 70, 440, 250, "Test accuracy per model (bar chart)")
text(500, 300, "Results (model_results.csv)", 15, "Helvetica-Bold", BLUE)
bullets([
    "Logistic Regression: [XX%]",
    "SVM: [XX%]",
    "Decision Tree: [XX%]",
    "KNN: [XX%]",
    "Best model: [name]",
], x=500, y=275, width=420, size=14)

# 20 --------------------------------------------------------------- Confusion matrix
new_slide("Predictive Analysis - Confusion Matrix of Best Model")
picture("cm_best.png", 30, 90, 440, 330, "Confusion matrix (best model)")
bullets([
    "Best model: [name] with tuned parameters [params].",
    "Confusion matrix: TP [n], TN [n], FP [n], FN [n] - describe which error type dominates.",
    "Test set is small ([n] launches), so differences between models may be within noise.",
], x=500, y=H - 120, width=420, size=14)

# 21 --------------------------------------------------------------- Conclusion
new_slide("Conclusion and Insights")
bullets([
    "Landing success is predictable from pre-launch features (orbit, site, payload, flight number, booster reuse).",
    "Success rate rose strongly over time as SpaceX gained experience and improved boosters.",
    "Launch site and orbit matter; sites near the coast with strong logistics concentrate the successful launches.",
    "Best model: [name], test accuracy [XX%]; all four models perform similarly, so a simple model is enough.",
    "Innovative next steps: add weather, booster-age and landing-pad data; use ensemble models (Random Forest, XGBoost); "
    "convert predicted landing probability into an expected cost per launch for bidding.",
], size=15)

c.save()
print("Saved", OUT, "-", page[0], "slides")
