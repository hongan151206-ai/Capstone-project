"""Build 'Data Science Capstone Project Report' slides (PDF, 16:9) - số liệu và ảnh lấy tự động từ output của 01-08.
Usage: python build_report.py [output.pdf]      (chạy sau run_all.py / sau khi đã chạy 01-08)
"""
import json
import math
import os
import sys
import pandas as pd
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfgen import canvas

W, H = 960, 540
NAVY, BLUE, LIGHT, GREY = HexColor("#0B2545"), HexColor("#1F6FB2"), HexColor("#EAF2FA"), HexColor("#6B7785")
GITHUB = "https://github.com/hongan151206-ai/Capstone-project"
OUT = sys.argv[1] if len(sys.argv) > 1 else "Data_Science_Capstone_Project_Report.pdf"
MISSING = []


# ----------------------------------------------------------------------------- load results
def jload(f):
    try:
        return json.load(open(f))
    except Exception:
        MISSING.append(f); return {}


def csv1(f):
    try:
        return pd.read_csv(f)
    except Exception:
        MISSING.append(f); return pd.DataFrame()


R, FOL, DSH = jload("results.json"), jload("folium_results.json"), jload("dash_results.json")
df = csv1("dataset_part_2.csv")
SQL = {i: csv1(f"sql_results/q{i}.csv") for i in range(1, 11)}


def pct(x):
    return f"{100 * x:.1f}%"


def first(i, default="n/a"):
    try:
        v = SQL[i].iloc[0, 0]
        return f"{v:,.0f}" if isinstance(v, float) else v
    except Exception:
        return default


# ----------------------------------------------------------------------------- derived facts from dataset_part_2
F = {}
if len(df):
    df["Year"] = pd.to_datetime(df["Date"]).dt.year
    F["n"] = len(df); F["rate"] = df["Class"].mean()
    yr = df.groupby("Year")["Class"].mean()
    F["yr_first"], F["yr_last"] = (yr.index[0], yr.iloc[0]), (yr.index[-1], yr.iloc[-1])
    F["yr_peak"] = (yr.idxmax(), yr.max())
    med = df["FlightNumber"].median()
    F["early"], F["late"] = df[df["FlightNumber"] <= med]["Class"].mean(), df[df["FlightNumber"] > med]["Class"].mean()
    F["med"] = int(med)
    site = df.groupby("LaunchSite")["Class"].agg(["mean", "count"]).sort_values("mean", ascending=False)
    F["site_best"], F["site_worst"] = site.index[0], site.index[-1]; F["site"] = site
    orb = df.groupby("Orbit")["Class"].agg(["mean", "count"]).sort_values("mean", ascending=False)
    F["orb"] = orb; big = orb[orb["count"] >= 8]
    F["orb_best_big"] = big.index[0] if len(big) else orb.index[0]
    F["orb_worst_big"] = big.index[-1] if len(big) else orb.index[-1]
    F["pay_low"] = df[df["PayloadMass"] < 5000]["Class"].mean(); F["pay_high"] = df[df["PayloadMass"] >= 5000]["Class"].mean()
    F["miss"] = df.isnull().sum(); F["outcomes"] = df["Outcome"].value_counts()
    F["site_counts"] = df["LaunchSite"].value_counts(); F["orbit_counts"] = df["Orbit"].value_counts()


def f(key, default="n/a"):
    return F.get(key, default)


# ----------------------------------------------------------------------------- drawing helpers
c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("Data Science Capstone Project Report")
page = [0]


def new_slide(title):
    if page[0]:
        c.showPage()
    page[0] += 1
    c.setFillColor(NAVY); c.rect(0, H - 70, W, 70, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 24); c.drawString(36, H - 45, title)
    c.setFillColor(BLUE); c.setFont("Helvetica", 10); c.drawString(36, 14, f"GitHub: {GITHUB}")
    c.linkURL(GITHUB, (36, 8, 400, 26), relative=0)
    c.setFillColor(GREY); c.drawRightString(W - 30, 14, str(page[0]))


def text(x, y, s, size=15, font="Helvetica", color=black, width=None):
    c.setFillColor(color); c.setFont(font, size)
    for ln in (simpleSplit(s, font, size, width) if width else [s]):
        c.drawString(x, y, ln); y -= size * 1.3
    return y


def bullets(items, x=40, y=H - 108, width=W - 80, size=15, gap=7):
    for it in items:
        sub = it.startswith("- ")
        s = it[2:] if sub else it
        xx = x + (22 if sub else 0); fs = size - (2 if sub else 0)
        c.setFillColor(BLUE if not sub else GREY); c.circle(xx + 4, y + fs * 0.32, 2.6, fill=1, stroke=0)
        y = text(xx + 15, y, s, fs, width=width - (xx - x) - 15) - gap
    return y


def box(x, y, w, h, s, size=11):
    c.setFillColor(LIGHT); c.setStrokeColor(BLUE); c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setFillColor(NAVY); c.setFont("Helvetica", size)
    lines = simpleSplit(s, "Helvetica", size, w - 12); ty = y + h / 2 + (len(lines) - 1) * size * 0.6 - size * 0.3
    for ln in lines:
        c.drawCentredString(x + w / 2, ty, ln); ty -= size * 1.2


def arrow(x1, y1, x2, y2):
    c.setStrokeColor(GREY); c.setFillColor(GREY); c.setLineWidth(1.5); c.line(x1, y1, x2, y2)
    a = math.atan2(y2 - y1, x2 - x1); p = c.beginPath(); p.moveTo(x2, y2)
    p.lineTo(x2 - 9 * math.cos(a - .4), y2 - 9 * math.sin(a - .4)); p.lineTo(x2 - 9 * math.cos(a + .4), y2 - 9 * math.sin(a + .4))
    p.close(); c.drawPath(p, fill=1, stroke=0)


def flow(steps, y, bw=150, bh=62, gap=22, x=36):
    for i, s in enumerate(steps):
        box(x, y, bw, bh, s)
        if i < len(steps) - 1:
            arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2)
        x += bw + gap


def picture(fname, x, y, w, h, label=""):
    if os.path.exists(fname):
        img = ImageReader(fname); iw, ih = img.getSize(); r = min(w / iw, h / ih)
        c.drawImage(img, x + (w - iw * r) / 2, y + (h - ih * r) / 2, iw * r, ih * r)
    else:
        MISSING.append(fname)
        c.setStrokeColor(GREY); c.setDash(4, 3); c.rect(x, y, w, h, fill=0, stroke=1); c.setDash()
        c.setFillColor(GREY); c.setFont("Helvetica-Oblique", 11); c.drawCentredString(x + w / 2, y + h / 2, f"missing: {fname}")


def caption(s, y=58):
    text(40, y, s, 13, "Helvetica-Oblique", NAVY, width=W - 80)


def sqlbox(i, x, y, w, h):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    d = SQL.get(i)
    titles = {1: "Q1 Unique launch sites", 2: "Q2 Records for sites starting with 'CCA'", 3: "Q3 Total payload mass, NASA (CRS)",
              4: "Q4 Average payload mass, booster F9 v1.1", 5: "Q5 First successful ground-pad landing",
              6: "Q6 Drone-ship success, payload 4000-6000 kg", 7: "Q7 Successful vs failed missions",
              8: "Q8 Boosters carrying the maximum payload", 9: "Q9 2015 failed drone-ship landings",
              10: "Q10 Landing outcomes ranked, 2010-06-04 to 2017-03-20"}
    text(x, y + h - 12, titles[i], 11, "Helvetica-Bold", BLUE)
    if d is None or not len(d):
        return
    if i == 2:
        d = d[["Date", "Booster_Version", "Launch_Site", "Customer", "Landing_Outcome"]]
    d = d.copy()
    for col in d.columns:
        if d[col].dtype.kind == "f":
            d[col] = d[col].map(lambda v: f"{v:,.1f}")
    rows = d.astype(str).values.tolist(); cols = list(d.columns)
    maxrows = int((h - 30) // 14)
    more = len(rows) - maxrows
    rows = rows[:maxrows]
    fs = 9
    widths = [max([stringWidth(str(v), "Helvetica", fs) for v in [cols[k]] + [r[k] for r in rows]]) + 14 for k in range(len(cols))]
    scale = min(1, w / sum(widths)); widths = [wd * scale for wd in widths]
    yy = y + h - 30
    c.setFillColor(LIGHT); c.rect(x, yy - 3, sum(widths), 14, fill=1, stroke=0)
    xx = x
    for k, col in enumerate(cols):
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold", fs); c.drawString(xx + 3, yy, col[:int(widths[k] / 5)]); xx += widths[k]
    for r in rows:
        yy -= 14; xx = x
        for k, v in enumerate(r):
            v = v.strip(); lim = v
            while stringWidth(lim, "Helvetica", fs) > widths[k] - 6 and len(lim) > 3:
                lim = lim[:-2]
            if lim != v:
                lim = lim.rstrip() + ".."
            c.setFillColor(black); c.setFont("Helvetica", fs); c.drawString(xx + 3, yy, lim); xx += widths[k]
    if more > 0:
        text(x, yy - 14, f"... +{more} more rows (see sql_results/q{i}.csv)", 8, "Helvetica-Oblique", GREY)


# ============================================================================= SLIDES
# 1 Title
new_slide("Data Science Capstone Project Report")
text(40, H - 140, "Predicting SpaceX Falcon 9 First-Stage Landing Success", 28, "Helvetica-Bold", NAVY, width=W - 80)
text(40, H - 230, "IBM Applied Data Science Capstone", 18, color=GREY)
text(40, H - 262, "Author: Hong An Vo", 18, color=GREY)
text(40, H - 294, f"Project repository: {GITHUB}", 14, color=BLUE)

# 2 Executive summary
new_slide("Executive Summary")
best, acc = R.get("best_model", "n/a"), R.get("best_test_accuracy")
bullets([
    "Goal: predict whether a Falcon 9 first stage lands successfully, because reuse is what lets SpaceX price a launch at "
    "~$62M versus $165M+ for competitors.",
    "Methods: data from the SpaceX REST API and Wikipedia web scraping; wrangling with pandas (Class label); EDA with SQL "
    "and Seaborn/Matplotlib; Folium map and Plotly Dash dashboard; four classifiers (Logistic Regression, SVM, Decision Tree, KNN) "
    "tuned with GridSearchCV.",
    f"Key results: {f('n')} Falcon 9 launches, overall landing success rate {pct(f('rate', 0))}; success rose from "
    f"{pct(f('yr_first', (0, 0))[1])} in {f('yr_first', ('', 0))[0]} to {pct(f('yr_last', (0, 0))[1])} in {f('yr_last', ('', 0))[0]}; "
    f"best model: {best} with {pct(acc) if acc is not None else 'n/a'} test accuracy.",
    f"Conclusion: landing outcome is predictable from pre-launch features; flight experience, orbit and launch site "
    f"drive success. Illustrative expected launch cost from predicted landing probability: ~${R.get('expected_cost_musd', 'n/a')}M.",
], size=15, gap=10)

# 3 Introduction
new_slide("Introduction")
text(40, H - 105, "Project background", 18, "Helvetica-Bold", BLUE)
y = bullets([
    "Commercial space travel is growing and SpaceX leads the field thanks to reusable rockets.",
    "A Falcon 9 launch is advertised at ~$62M; other providers charge upwards of $165M. Most of the saving comes from reusing the first stage.",
], y=H - 135)
text(40, y - 4, "Problem statement", 18, "Helvetica-Bold", BLUE)
bullets([
    "We work as a data scientist for a company that wants to bid against SpaceX for a rocket launch.",
    "Task: determine the price of each launch by predicting whether the first stage will land successfully (and so be reused).",
    "Questions: what factors determine landing success? how did success change over time? which classifier predicts best?",
], y=y - 34)

# 4 API
new_slide("Data Collection - SpaceX API")
text(40, H - 100, "Flowchart", 16, "Helvetica-Bold", BLUE)
flow(["GET api.spacexdata.com /v4/launches/past", "Normalize JSON (pandas)", "Filter: 1 core, 1 payload, date <= 2020-11-13",
      "Call /rockets /launchpads /payloads /cores", "Build DataFrame, keep Falcon 9 only"], H - 190)
bullets([
    "Key phrases: requests.get() -> .json() -> json_normalize() -> helper functions per endpoint",
    "Helpers: getBoosterVersion, getLaunchSite, getPayloadData, getCoreData",
    "Missing PayloadMass replaced with the column mean; Falcon 1 launches removed; FlightNumber re-indexed",
    f"Result: dataset_part_1.csv with {f('n')} Falcon 9 launches and 17 columns (Orbit, LaunchSite, Outcome, GridFins, Reused, Legs, ...)",
    "Code: 01_spacex_api_collection.py",
], y=H - 250, size=14, gap=6)

# 5 Scraping
new_slide("Data Collection - Web Scraping")
text(40, H - 100, "Flowchart", 16, "Helvetica-Bold", BLUE)
flow(["Request Wikipedia: List of Falcon 9 and Falcon Heavy launches", "Parse HTML with BeautifulSoup", "Locate launch tables (wikitable)",
      "Extract each row with helper functions", "Save DataFrame to CSV"], H - 190)
bullets([
    "Key phrases: requests.get() -> BeautifulSoup() -> find_all('table') -> parse <th>/<td> cells",
    "Fields: flight no., launch site, payload, mass, orbit, customer, launch outcome, booster version, landing outcome, date, time",
    "Helpers clean date/time, booster version, landing status and payload mass strings",
    "Output: spacex_web_scraped.csv; used to cross-check the API data",
    "Code: 02_web_scraping.py",
], y=H - 250, size=14, gap=6)

# 6 Wrangling
new_slide("Data Wrangling Methodology")
bullets([
    "Checked missing values and data types per column.",
    "Counted launches per site, per orbit and each landing outcome (True/False + Ocean, RTLS, ASDS; None = not attempted).",
    "Label: Class = 0 for bad outcomes (False Ocean, False RTLS, False ASDS, None ASDS, None None), otherwise 1.",
    "Feature table: one-hot encoding of Orbit, LaunchSite, LandingPad, Serial -> dataset_part_3.csv.",
    "Code: 03_data_wrangling.py, 05_eda_visualization.py",
], width=470, size=13, gap=6)
if len(df):
    x0 = 540; text(x0, H - 105, "Results on the cleaned data", 15, "Helvetica-Bold", BLUE)
    lines = [f"Launches: {F['n']}   |   success rate (Class=1): {pct(F['rate'])}"]
    lines += ["Launches per site:"] + [f"   {k}: {v}" for k, v in F["site_counts"].items()]
    lines += ["Top orbits: " + ", ".join(f"{k} ({v})" for k, v in list(F["orbit_counts"].items())[:5])]
    lines += ["Landing outcomes: " + ", ".join(f"{k} ({v})" for k, v in list(F["outcomes"].items())[:5])]
    miss = F["miss"][F["miss"] > 0]
    lines += ["Missing values: " + (", ".join(f"{k} ({v})" for k, v in miss.items()) if len(miss) else "none after cleaning")]
    yy = H - 128
    for ln in lines:
        yy = text(x0, yy, ln, 11, width=380) - 3

# 7 EDA viz methodology
new_slide("EDA with Data Visualization - Methodology")
bullets([
    "Scatter plots (Seaborn catplot, hue = Class): Flight Number vs Payload Mass; Flight Number vs Launch Site; Payload Mass vs Launch Site.",
    "Scatter plots: Flight Number vs Orbit; Payload Mass vs Orbit - orbit-specific behaviour.",
    "Bar chart: success rate per orbit - which orbit types are easiest to land.",
    "Line chart: yearly average success rate - learning curve over time.",
    "Purpose: reveal how each feature relates to landing success, choose features for the models, and spot sparse categories.",
    "Code: 05_eda_visualization.py",
], size=18, gap=14)

# 8 EDA SQL methodology
new_slide("EDA with SQL - Queries Performed")
bullets([
    "Loaded Spacex.csv into a SQLite table SPACEXTBL and ran 10 queries:",
    "- Q1-Q2: unique launch sites; 5 records for sites starting with 'CCA'",
    "- Q3-Q4: total payload for NASA (CRS); average payload for booster F9 v1.1",
    "- Q5-Q6: first successful ground-pad landing; boosters with drone-ship success and 4000-6000 kg payload",
    "- Q7-Q8: successful vs failed missions; boosters carrying the maximum payload",
    "- Q9-Q10: failed drone-ship landings in 2015; ranking of landing outcomes 2010-06-04 to 2017-03-20",
    "Code: 04_eda_sql.py (results saved as sql_results/q1..q10.csv)",
], size=18, gap=12)

# 9 Interactive analytics methodology
new_slide("Interactive Visual Analytics - Folium and Plotly Dash")
text(40, H - 105, "Folium map (06_folium_map.py)", 17, "Helvetica-Bold", BLUE)
y = bullets([
    "Circle + label for each launch site; marker clusters coloured green (success) / red (failure).",
    "MousePosition to pick coordinates; PolyLines with distance (haversine) to coastline, railway, highway and nearest city.",
], y=H - 135, size=14, gap=5)
text(40, y - 4, "Plotly Dash app (07_dash_app.py)", 17, "Helvetica-Bold", BLUE)
y = bullets([
    "Dropdown (all sites or one site) drives a pie chart of successful launches / success vs failure.",
    "Range slider filters payload mass; scatter plot of payload vs outcome coloured by booster version category.",
], y=y - 34, size=14, gap=5)
text(40, y - 6, f"GitHub (Folium + Dash code): {GITHUB}", 12, color=BLUE)

# 10 Predictive method
new_slide("Predictive Analysis (Classification) - Methodology")
bullets([
    "Target: Class (1 = first stage landed). Features: dataset_part_3 (one-hot encoded), standardised with StandardScaler.",
    f"Split: 80% train / 20% test (random_state = 2) -> {R.get('n_train', 'n/a')} train, {R.get('n_test', 'n/a')} test launches.",
    "Models: Logistic Regression, Support Vector Machine, Decision Tree, K-Nearest Neighbours.",
    "Tuning: GridSearchCV with 10-fold cross-validation (C/penalty; kernel/C/gamma; criterion/depth/leaf; n_neighbors/algorithm/p).",
    "Evaluation: test accuracy, precision, recall, F1 and confusion matrix; best model chosen on test accuracy (ties -> CV accuracy).",
    "Code: 08_predictive_analysis.py",
], size=18, gap=14)

# 11-13 EDA visualization results
new_slide("EDA Results - Scatter Plots (Flight Number, Payload, Site)")
picture("viz_flight_payload.png", 30, 100, 440, 320); picture("viz_flight_site.png", 490, 100, 440, 320)
caption(f"Success rate is {pct(f('early', 0))} for flights 1-{f('med')} and {pct(f('late', 0))} after that. "
        f"Payloads under 5000 kg land {pct(f('pay_low', 0))} of the time vs {pct(f('pay_high', 0))} for heavier loads. "
        f"Best site: {f('site_best')}.", y=84)

new_slide("EDA Results - Payload by Site and Orbit")
picture("viz_payload_site.png", 30, 100, 440, 320); picture("viz_payload_orbit.png", 490, 100, 440, 320)
caption(f"Payloads under 5000 kg: {pct(f('pay_low', 0))} success; 5000 kg and above: {pct(f('pay_high', 0))}. "
        f"Best site by success rate: {f('site_best')}; weakest: {f('site_worst')}.", y=84)

new_slide("EDA Results - Orbit Analysis")
picture("viz_flight_orbit.png", 30, 100, 440, 320); picture("viz_success_by_orbit.png", 490, 100, 440, 320)
try:
    o = F["orb"]
    caption("Orbits with 100% success have very few launches (" + ", ".join(f"{k}: {int(r['count'])}" for k, r in o[o["mean"] == 1].iterrows()) +
            f"); among orbits with at least 8 launches the best is {f('orb_best_big')} and the weakest is {f('orb_worst_big')}.", y=84)
except Exception:
    pass

new_slide("EDA Results - Yearly Trend")
picture("viz_yearly_trend.png", 30, 80, 560, 350)
try:
    yr_ = df.groupby("Year")["Class"].agg(["mean", "count"])
    text(620, H - 105, "Success rate by year (launches)", 13, "Helvetica-Bold", BLUE)
    yy = H - 128
    for k, r in yr_.iterrows():
        yy = text(620, yy, f"{k}:  {pct(r['mean'])}   ({int(r['count'])})", 12) - 2
except Exception:
    pass
caption(f"Success rate moved from {pct(f('yr_first', (0, 0))[1])} ({f('yr_first', ('', 0))[0]}) to {pct(f('yr_last', (0, 0))[1])} "
        f"({f('yr_last', ('', 0))[0]}), peaking at {pct(f('yr_peak', (0, 0))[1])} in {f('yr_peak', ('', 0))[0]}.", y=60)

# 14-16 SQL results
new_slide("EDA with SQL - Launch Sites and Payloads (Q1-Q4)")
sqlbox(1, 30, 255, 440, 170); sqlbox(2, 490, 255, 440, 170)
sqlbox(3, 30, 90, 440, 150); sqlbox(4, 490, 90, 440, 150)
caption(f"NASA (CRS) carried {first(3)} kg in total; boosters F9 v1.1 averaged {first(4)} kg per launch.", y=64)

new_slide("EDA with SQL - Landing Success and Mission Outcomes (Q5-Q8)")
sqlbox(5, 30, 255, 440, 170); sqlbox(6, 490, 255, 440, 170)
sqlbox(7, 30, 90, 440, 150); sqlbox(8, 490, 90, 440, 150)
caption(f"First successful ground-pad landing: {first(5)}. Boosters that landed on a drone ship with 4000-6000 kg payloads and the "
        f"boosters that carried the maximum payload are listed above.", y=64)

new_slide("EDA with SQL - Rankings and Time Analysis (Q9-Q10)")
sqlbox(9, 30, 255, 440, 170); sqlbox(10, 490, 215, 440, 210)
try:
    top = SQL[10].iloc[0]
    caption(f"Most frequent outcome between 2010-06-04 and 2017-03-20: '{top.iloc[0]}' ({top.iloc[1]} launches). "
            "Failed drone-ship landings in 2015 versus successful landings later show the landing technology maturing over time.", y=150)
except Exception:
    pass

# 17-18 Folium
new_slide("Folium Map - Launch Sites and Launch Records")
picture("folium_sites.png", 30, 100, 440, 320); picture("folium_clusters.png", 490, 100, 440, 320)
try:
    st = pd.DataFrame(FOL["site_stats"])
    caption("Launch sites: " + "; ".join(f"{r['Launch Site']} {int(r['sum'])}/{int(r['count'])} ({pct(r['rate'])})" for _, r in st.iterrows()) +
            ". Sites are on the US coasts (Florida, California); clusters are coloured green/red per launch.", y=84)
except Exception:
    pass

new_slide("Folium Map - Proximity Analysis")
picture("folium_proximity.png", 30, 90, 540, 340)
d = FOL.get("distances_km", {})
bullets([f"{k}: {v:.2f} km" for k, v in d.items()] +
        ["Close to coast, railway and highway: easy transport of rocket parts and safe launches over the ocean.",
         "Far from cities: limits risk to the population."], x=590, y=H - 120, width=340, size=13)

# 19-20 Dash
new_slide("Plotly Dash - Success Pie Charts")
picture("dash_pie_all.png", 30, 100, 440, 320); picture("dash_pie_site.png", 490, 100, 440, 320)
caption(f"{DSH.get('site_most_successes', 'n/a')} accounts for the largest share of successful launches; "
        f"{DSH.get('site_best_rate', 'n/a')} has the best success ratio (right pie).", y=84)

new_slide("Plotly Dash - Payload vs Launch Outcome")
picture("dash_scatter_all.png", 30, 100, 440, 320); picture("dash_scatter_range.png", 490, 100, 440, 320)
caption(f"Success rate is {pct(DSH.get('rate_payload_lt5000', 0))} for payloads under 5000 kg vs {pct(DSH.get('rate_payload_ge5000', 0))} above; "
        "by booster version: " + ", ".join(f"{k} {pct(v)}" for k, v in DSH.get("rate_by_booster_category", {}).items()) + ".", y=84)

# 21-22 Predictive results
new_slide("Predictive Analysis Results - Model Comparison")
picture("model_comparison.png", 20, 110, 400, 300)
yy = H - 105
text(440, yy, "Model | CV acc | Test acc | Precision | Recall | F1", 12, "Helvetica-Bold", BLUE); yy -= 22
for r in R.get("table", []):
    yy = text(440, yy, f"{r['Model']:<20} {r['CV accuracy']:.3f}   {r['Test accuracy']:.3f}   {r['Precision']:.3f}   {r['Recall']:.3f}   {r['F1']:.3f}", 11) - 8
bullets([f"Best model: {best} - test accuracy {pct(acc) if acc is not None else 'n/a'}",
         f"Best parameters: {R.get('best_params', 'n/a')}"], x=440, y=yy - 14, width=490, size=12)

new_slide("Predictive Analysis Results - Confusion Matrix and Best Model")
picture("cm_best.png", 20, 150, 330, 270); picture("feature_importance.png", 370, 150, 330, 270)
cb = R.get("confusion_best", {})
bullets([
    f"{best}: TP {cb.get('TP', 'n/a')}, TN {cb.get('TN', 'n/a')}, FP {cb.get('FP', 'n/a')}, FN {cb.get('FN', 'n/a')} on {R.get('n_test', 'n/a')} test launches.",
    "FP = predicted a landing that did not happen; FN = missed a successful landing.",
    f"Strongest features (logistic regression coefficients): {', '.join(R.get('top_features', {}).keys())}.",
], x=720, y=H - 110, width=215, size=11, gap=5)
caption(f"Test set is small ({R.get('n_test', 'n/a')} launches), so differences between models are within noise; "
        "compare the models on the F1 score and the confusion matrix as well as accuracy.", y=100)

# 23 Conclusion
new_slide("Conclusion and Innovative Insights")
bullets([
    f"Landing success is predictable from pre-launch data: {best} reaches {pct(acc) if acc is not None else 'n/a'} test accuracy.",
    f"Success changed from {pct(f('yr_first', (0, 0))[1])} to {pct(f('yr_last', (0, 0))[1])} across years; "
    f"later flights succeed {pct(f('late', 0))} of the time vs {pct(f('early', 0))} for early ones.",
    f"Orbit and site matter: best site {f('site_best')}; payloads below 5000 kg land {pct(f('pay_low', 0))} vs {pct(f('pay_high', 0))}.",
    f"Innovative insight - cost model: converting predicted landing probability into expected cost (assumption: "
    f"${R.get('cost_assumption', ['62', '165'])[0]}M if landed, ${R.get('cost_assumption', ['62', '165'])[1]}M if not) gives about "
    f"${R.get('expected_cost_musd', 'n/a')}M per launch, a basis for a competing bid.",
    "Next steps: add weather, booster age and landing-pad data; try ensembles (Random Forest, XGBoost); validate with launches after 2020.",
], size=14, gap=9)

c.save()
print("Saved", OUT, "-", page[0], "slides")
if MISSING:
    print("WARNING - missing inputs (chạy lại các bước 01-08):", sorted(set(MISSING)))
