"""4. EDA with SQL (SQLite, bảng SPACEXTBL)"""
import sqlite3
import pandas as pd

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/labs/module_2/data/Spacex.csv")

QUERIES = {
    "Q1 Unique launch sites":
        "SELECT DISTINCT Launch_Site FROM SPACEXTBL",
    "Q2 5 records, site begins with 'CCA'":
        "SELECT * FROM SPACEXTBL WHERE Launch_Site LIKE 'CCA%' LIMIT 5",
    "Q3 Total payload mass for NASA (CRS)":
        "SELECT SUM(PAYLOAD_MASS__KG_) AS total_kg FROM SPACEXTBL WHERE Customer = 'NASA (CRS)'",
    "Q4 Avg payload mass, booster F9 v1.1":
        "SELECT AVG(PAYLOAD_MASS__KG_) AS avg_kg FROM SPACEXTBL WHERE Booster_Version LIKE 'F9 v1.1%'",
    "Q5 First successful ground-pad landing date":
        "SELECT MIN(Date) FROM SPACEXTBL WHERE Landing_Outcome = 'Success (ground pad)'",
    "Q6 Drone-ship success, payload 4000-6000 kg":
        "SELECT DISTINCT Booster_Version FROM SPACEXTBL WHERE Landing_Outcome = 'Success (drone ship)' "
        "AND PAYLOAD_MASS__KG_ > 4000 AND PAYLOAD_MASS__KG_ < 6000",
    "Q7 Total successful vs failed missions":
        "SELECT Mission_Outcome, COUNT(*) AS n FROM SPACEXTBL GROUP BY Mission_Outcome",
    "Q8 Boosters carrying max payload":
        "SELECT DISTINCT Booster_Version FROM SPACEXTBL WHERE PAYLOAD_MASS__KG_ = "
        "(SELECT MAX(PAYLOAD_MASS__KG_) FROM SPACEXTBL)",
    "Q9 2015 failed drone-ship landings (month, booster, site)":
        "SELECT substr(Date,6,2) AS month, Booster_Version, Launch_Site FROM SPACEXTBL "
        "WHERE Landing_Outcome = 'Failure (drone ship)' AND substr(Date,1,4) = '2015'",
    "Q10 Rank landing outcomes 2010-06-04..2017-03-20":
        "SELECT Landing_Outcome, COUNT(*) AS n FROM SPACEXTBL "
        "WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' "
        "GROUP BY Landing_Outcome ORDER BY n DESC",
}


def table_png(df, title, fname):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = df.head(12).copy()
    for col in d.columns:
        if d[col].dtype.kind == "f":
            d[col] = d[col].round(1)
    d = d.astype(str)
    fig, ax = plt.subplots(figsize=(9, 0.45 * (len(d) + 2) + 0.4))
    ax.axis("off"); ax.set_title(title, fontsize=11, loc="left")
    t = ax.table(cellText=d.values, colLabels=list(d.columns), loc="center", cellLoc="left")
    t.auto_set_font_size(False); t.set_fontsize(10); t.scale(1, 1.5); t.auto_set_column_width(list(range(len(d.columns))))
    fig.savefig(fname, dpi=150, bbox_inches="tight"); plt.close(fig)


def fix_date(s):
    s = s.astype(str)
    iso = s.str.match(r"^\d{4}-")
    return pd.to_datetime(s, dayfirst=not iso.all(), errors="coerce").dt.strftime("%Y-%m-%d")


def main():
    import os
    os.makedirs("sql_results", exist_ok=True)
    df = pd.read_csv(URL)
    df.columns = [c.strip().replace(" _", "_") for c in df.columns]
    df = df.rename(columns={"Time (UTC)": "Time_UTC"})
    df["Date"] = fix_date(df["Date"])

    con = sqlite3.connect("my_data1.db")
    df.to_sql("SPACEXTBL", con, if_exists="replace", index=False)

    for i, (title, q) in enumerate(QUERIES.items(), 1):
        res = pd.read_sql_query(q, con)
        print(f"\n=== {title} ===")
        print(res.to_string(index=False))
        res.to_csv(f"sql_results/q{i}.csv", index=False)
        table_png(res, title, f"sql_q{i}.png")
    con.close()


if __name__ == "__main__":
    main()
