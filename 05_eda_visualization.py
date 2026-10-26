"""5. EDA with Data Visualization  ->  PNG charts + dataset_part_3.csv (one-hot features)"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")


def cat(x, y, hue, fname, xl, yl):
    g = sns.catplot(y=y, x=x, hue=hue, data=df, aspect=3)
    g.set_axis_labels(xl, yl)
    g.savefig(fname, dpi=150); plt.close("all")


def main():
    global df
    try:
        df = pd.read_csv("dataset_part_2.csv")
    except FileNotFoundError:
        df = pd.read_csv(URL)
    sns.set_theme(style="whitegrid")

    # Scatter plots
    cat("FlightNumber", "PayloadMass", "Class", "viz_flight_payload.png", "Flight Number", "Payload Mass (kg)")
    cat("FlightNumber", "LaunchSite", "Class", "viz_flight_site.png", "Flight Number", "Launch Site")
    cat("PayloadMass", "LaunchSite", "Class", "viz_payload_site.png", "Payload Mass (kg)", "Launch Site")
    cat("FlightNumber", "Orbit", "Class", "viz_flight_orbit.png", "Flight Number", "Orbit")
    cat("PayloadMass", "Orbit", "Class", "viz_payload_orbit.png", "Payload Mass (kg)", "Orbit")

    # Bar chart: success rate per orbit
    orbit_rate = df.groupby("Orbit")["Class"].mean().sort_values(ascending=False)
    plt.figure(figsize=(9, 4)); sns.barplot(x=orbit_rate.index, y=orbit_rate.values, color="#1f77b4")
    plt.ylabel("Success rate"); plt.xlabel("Orbit"); plt.title("Success rate by orbit")
    plt.tight_layout(); plt.savefig("viz_success_by_orbit.png", dpi=150); plt.close()

    # Yearly trend
    df["Year"] = pd.to_datetime(df["Date"]).dt.year
    yearly = df.groupby("Year")["Class"].mean()
    plt.figure(figsize=(8, 4)); plt.plot(yearly.index, yearly.values, marker="o")
    plt.xlabel("Year"); plt.ylabel("Success rate"); plt.title("Launch success rate by year")
    plt.grid(True); plt.tight_layout(); plt.savefig("viz_yearly_trend.png", dpi=150); plt.close()

    # Feature engineering -> dataset_part_3.csv
    features = df[["FlightNumber", "PayloadMass", "Orbit", "LaunchSite", "Flights", "GridFins",
                   "Reused", "Legs", "LandingPad", "Block", "ReusedCount", "Serial"]]
    features_one_hot = pd.get_dummies(features, columns=["Orbit", "LaunchSite", "LandingPad", "Serial"])
    features_one_hot = features_one_hot.astype("float64")
    features_one_hot.to_csv("dataset_part_3.csv", index=False)
    print("Saved charts and dataset_part_3.csv", features_one_hot.shape)


if __name__ == "__main__":
    main()
