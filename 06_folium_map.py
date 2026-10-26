"""6. Interactive Map with Folium  ->  spacex_map.html"""
from math import sin, cos, sqrt, atan2, radians
import pandas as pd
import folium
from folium.plugins import MarkerCluster, MousePosition
from folium.features import DivIcon

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv")


def distance_km(lat1, lon1, lat2, lon2):
    R = 6373.0
    dlon, dlat = radians(lon2 - lon1), radians(lat2 - lat1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def main():
    df = pd.read_csv(URL)[["Launch Site", "Lat", "Long", "class"]]
    sites = df.groupby("Launch Site", as_index=False).first()[["Launch Site", "Lat", "Long"]]

    m = folium.Map(location=[29.559684888503615, -95.0830971930759], zoom_start=5)

    # Task 1: marker + circle + label cho từng launch site
    for _, r in sites.iterrows():
        pt = [r["Lat"], r["Long"]]
        folium.Circle(pt, radius=1000, color="#d35400", fill=True).add_child(folium.Popup(r["Launch Site"])).add_to(m)
        folium.map.Marker(pt, icon=DivIcon(
            icon_size=(20, 20), icon_anchor=(0, 0),
            html=f'<div style="font-size:12;color:#d35400;"><b>{r["Launch Site"]}</b></div>')).add_to(m)

    # Task 2: marker cluster - xanh = success, đỏ = failure
    cluster = MarkerCluster().add_to(m)
    df["color"] = df["class"].map({1: "green", 0: "red"})
    for _, r in df.iterrows():
        folium.Marker([r["Lat"], r["Long"]],
                      icon=folium.Icon(color="white", icon_color=r["color"]),
                      popup=f'{r["Launch Site"]}: {"Success" if r["class"] else "Failure"}').add_to(cluster)

    MousePosition(position="topright", separator=" Long: ", empty_string="NaN", lng_first=False,
                  num_digits=20, prefix="Lat:").add_to(m)

    # Task 3: khoảng cách tới coastline / city / railway / highway (toạ độ lấy bằng MousePosition)
    # Ví dụ cho CCAFS SLC-40: điều chỉnh toạ độ theo điểm bạn chọn trên bản đồ
    site = sites[sites["Launch Site"].str.contains("CCAFS SLC-40")].iloc[0]
    proximities = {
        "Coastline": (28.56342, -80.56794),
        "Railway":   (28.57206, -80.58528),
        "Highway":   (28.56410, -80.57070),
        "City (Melbourne)": (28.10473, -80.64532),
    }
    for name, (lat, lon) in proximities.items():
        d = distance_km(site["Lat"], site["Long"], lat, lon)
        folium.Marker([lat, lon], icon=DivIcon(
            icon_size=(20, 20), icon_anchor=(0, 0),
            html=f'<div style="font-size:12;color:#1f77b4;"><b>{name}: {d:.2f} KM</b></div>')).add_to(m)
        folium.PolyLine([[site["Lat"], site["Long"]], [lat, lon]], weight=1).add_to(m)
        print(f"{name}: {d:.2f} km")

    m.save("spacex_map.html")


if __name__ == "__main__":
    main()
