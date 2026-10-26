"""7b. Static versions of the Dash charts (for slides) -> dash_*.png + dash_results.json"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")


def scatter(d, title, fname):
    fig, ax = plt.subplots(figsize=(7, 5))
    for cat, g in d.groupby("Booster Version Category"):
        ax.scatter(g["Payload Mass (kg)"], g["class"], label=cat, alpha=.8)
    ax.set_xlabel("Payload Mass (kg)"); ax.set_ylabel("class (1 = success)"); ax.set_yticks([0, 1])
    ax.set_title(title); ax.legend(title="Booster version", fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(fname, dpi=150); plt.close(fig)


def main():
    df = pd.read_csv(URL)
    by_site = df.groupby("Launch Site")["class"].agg(["sum", "count"])
    by_site["rate"] = by_site["sum"] / by_site["count"]
    best_share = by_site["sum"].idxmax()
    best_rate = by_site["rate"].idxmax()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(by_site["sum"], labels=by_site.index, autopct="%1.1f%%", textprops={"fontsize": 8})
    ax.set_title("Total successful launches by site"); fig.tight_layout()
    fig.savefig("dash_pie_all.png", dpi=150); plt.close(fig)

    vc = df[df["Launch Site"] == best_rate]["class"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(vc.values, labels=["Failure" if i == 0 else "Success" for i in vc.index], autopct="%1.1f%%",
           colors=["#d62728" if i == 0 else "#2ca02c" for i in vc.index])
    ax.set_title(f"Success vs failure - {best_rate}"); fig.tight_layout()
    fig.savefig("dash_pie_site.png", dpi=150); plt.close(fig)

    scatter(df, "Payload vs launch outcome (all sites, all payloads)", "dash_scatter_all.png")
    lo, hi = 2000, 6000
    rng = df[(df["Payload Mass (kg)"] >= lo) & (df["Payload Mass (kg)"] <= hi)]
    scatter(rng, f"Payload vs outcome, slider range {lo}-{hi} kg", "dash_scatter_range.png")

    low = df[df["Payload Mass (kg)"] < 5000]["class"].mean()
    high = df[df["Payload Mass (kg)"] >= 5000]["class"].mean()
    cat_rate = df.groupby("Booster Version Category")["class"].mean().round(3).to_dict()
    json.dump({"site_most_successes": best_share, "site_best_rate": best_rate,
               "site_table": by_site.round(3).reset_index().to_dict("records"),
               "range_slider": [lo, hi], "rate_payload_lt5000": round(low, 3),
               "rate_payload_ge5000": round(high, 3), "rate_by_booster_category": cat_rate},
              open("dash_results.json", "w"), indent=2)
    print(by_site)


if __name__ == "__main__":
    main()
