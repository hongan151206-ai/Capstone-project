"""6. Interactive Map with Folium -> spacex_map.html  (+ static PNG figures for the slides)"""
import json
from math import sin, cos, sqrt, atan2, radians
import pandas as pd
import folium
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster, MousePosition
from folium.features import DivIcon

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv")

# Toạ độ gần đúng quanh CCAFS SLC-40 (chọn bằng MousePosition trên bản đồ) - kiểm tra lại nếu muốn chính xác hơn
PROXIMITIES = {
    "Coastline": (28.56342, -80.56794),
    "Railway": (28.57206, -80.58528),
    "Highway": (28.56410, -80.57070),
    "City (Melbourne)": (28.10473, -80.64532),
}


def distance_km(lat1, lon1, lat2, lon2):
    R = 6373.0
    dlon, dlat = radians(lon2 - lon1), radians(lat2 - lat1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def main():
    df = pd.read_csv(URL)[["Launch Site", "Lat", "Long", "class"]]
    sites = df.groupby("Launch Site", as_index=False).first()[["Launch Site", "Lat", "Long"]]
    stats = df.groupby("Launch Site")["class"].agg(["sum", "count"]).reset_index()
    stats["failed"] = stats["count"] - stats["sum"]
    stats["rate"] = stats["sum"] / stats["count"]

    # ---------- Folium (HTML) ----------
    m = folium.Map(location=[29.559684888503615, -95.0830971930759], zoom_start=5)
    for _, r in sites.iterrows():
        pt = [r["Lat"], r["Long"]]
        folium.Circle(pt, radius=1000, color="#d35400", fill=True).add_child(folium.Popup(r["Launch Site"])).add_to(m)
        folium.map.Marker(pt, icon=DivIcon(
            icon_size=(20, 20), icon_anchor=(0, 0),
            html=f'<div style="font-size:12;color:#d35400;"><b>{r["Launch Site"]}</b></div>')).add_to(m)
    cluster = MarkerCluster().add_to(m)
    for _, r in df.iterrows():
        folium.Marker([r["Lat"], r["Long"]],
                      icon=folium.Icon(color="white", icon_color="green" if r["class"] else "red"),
                      popup=f'{r["Launch Site"]}: {"Success" if r["class"] else "Failure"}').add_to(cluster)
    MousePosition(position="topright", separator=" Long: ", empty_string="NaN", lng_first=False,
                  num_digits=20, prefix="Lat:").add_to(m)

    site = sites[sites["Launch Site"].str.contains("CCAFS SLC-40")].iloc[0]
    dist = {}
    for name, (lat, lon) in PROXIMITIES.items():
        d = distance_km(site["Lat"], site["Long"], lat, lon)
        dist[name] = round(d, 2)
        folium.Marker([lat, lon], icon=DivIcon(
            icon_size=(20, 20), icon_anchor=(0, 0),
            html=f'<div style="font-size:12;color:#1f77b4;"><b>{name}: {d:.2f} KM</b></div>')).add_to(m)
        folium.PolyLine([[site["Lat"], site["Long"]], [lat, lon]], weight=1).add_to(m)
    m.save("spacex_map.html")

    # ---------- Static figures for the report ----------
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(sites["Long"], sites["Lat"], s=120, color="#d35400")
    for k, (_, r) in enumerate(sites.iterrows()):
        ax.annotate(r["Launch Site"], (r["Long"], r["Lat"]), textcoords="offset points", xytext=(-90 if r["Long"] > -100 else 8, 8 + 12 * k), fontsize=8)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.set_title("SpaceX launch sites"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("folium_sites.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(stats))
    ax.bar(x, stats["sum"], color="green", label="Success")
    ax.bar(x, stats["failed"], bottom=stats["sum"], color="red", label="Failure")
    for i, r in stats.iterrows():
        ax.text(i, r["count"] + 0.3, f'{r["rate"]:.0%}', ha="center", fontsize=9)
    ax.set_xticks(list(x)); ax.set_xticklabels(stats["Launch Site"], rotation=15, fontsize=8)
    ax.set_ylabel("Launches"); ax.set_title("Launch records per site (label = success rate)"); ax.legend()
    fig.tight_layout(); fig.savefig("folium_clusters.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter([site["Long"]], [site["Lat"]], s=140, color="#d35400", zorder=3, label="CCAFS SLC-40")
    offsets = [(8, -14), (-100, 10), (8, 12), (8, 4)]
    for (name, (lat, lon)), off in zip(PROXIMITIES.items(), offsets):
        ax.plot([site["Long"], lon], [site["Lat"], lat], "-", color="grey", lw=1)
        ax.scatter([lon], [lat], s=50, color="#1f77b4", zorder=3)
        ax.annotate(f"{name}: {dist[name]:.2f} km", (lon, lat), textcoords="offset points", xytext=off, fontsize=9)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.set_title("Proximity of CCAFS SLC-40"); ax.grid(alpha=.3)
    ax.legend(loc="lower right")
    fig.tight_layout(); fig.savefig("folium_proximity.png", dpi=150); plt.close(fig)

    json.dump({"distances_km": dist, "site_stats": stats.round(3).to_dict("records")},
              open("folium_results.json", "w"), indent=2)
    print(dist)


if __name__ == "__main__":
    main()
