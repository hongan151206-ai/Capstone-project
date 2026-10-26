"""1. Data Collection - SpaceX REST API  ->  dataset_part_1.csv"""
import requests
import pandas as pd

# Snapshot cố định của IBM (kết quả ổn định, khớp đáp án lab)
STATIC_URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
              "IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json")
LIVE_URL = "https://api.spacexdata.com/v4/launches/past"

BoosterVersion, PayloadMass, Orbit, LaunchSite = [], [], [], []
Outcome, Flights, GridFins, Reused, Legs = [], [], [], [], []
LandingPad, Block, ReusedCount, Serial = [], [], [], []
Longitude, Latitude = [], []


def get(url):
    return requests.get(url, timeout=30).json()


def getBoosterVersion(data):
    for x in data["rocket"]:
        if x:
            BoosterVersion.append(get("https://api.spacexdata.com/v4/rockets/" + str(x))["name"])


def getLaunchSite(data):
    for x in data["launchpad"]:
        if x:
            r = get("https://api.spacexdata.com/v4/launchpads/" + str(x))
            Longitude.append(r["longitude"]); Latitude.append(r["latitude"]); LaunchSite.append(r["name"])


def getPayloadData(data):
    for load in data["payloads"]:
        if load:
            r = get("https://api.spacexdata.com/v4/payloads/" + load)
            PayloadMass.append(r["mass_kg"]); Orbit.append(r["orbit"])


def getCoreData(data):
    for core in data["cores"]:
        if core["core"] is not None:
            r = get("https://api.spacexdata.com/v4/cores/" + core["core"])
            Block.append(r["block"]); ReusedCount.append(r["reuse_count"]); Serial.append(r["serial"])
        else:
            Block.append(None); ReusedCount.append(None); Serial.append(None)
        Outcome.append(f"{core['landing_success']} {core['landing_type']}")
        Flights.append(core["flight"]); GridFins.append(core["gridfins"])
        Reused.append(core["reused"]); Legs.append(core["legs"]); LandingPad.append(core["landpad"])


def main():
    # Dùng snapshot tĩnh; đổi sang get(LIVE_URL) nếu muốn dữ liệu mới nhất
    data = pd.json_normalize(get(STATIC_URL))
    data = data[["rocket", "payloads", "launchpad", "cores", "flight_number", "date_utc"]]

    # Chỉ giữ launch có 1 core & 1 payload
    data = data[data["cores"].map(len) == 1]
    data = data[data["payloads"].map(len) == 1]
    data["cores"] = data["cores"].map(lambda x: x[0])
    data["payloads"] = data["payloads"].map(lambda x: x[0])

    data["date"] = pd.to_datetime(data["date_utc"]).dt.date
    data = data[data["date"] <= pd.to_datetime("2020-11-13").date()]

    getBoosterVersion(data); getLaunchSite(data); getPayloadData(data); getCoreData(data)

    launch_dict = {
        "FlightNumber": list(data["flight_number"]), "Date": list(data["date"]),
        "BoosterVersion": BoosterVersion, "PayloadMass": PayloadMass, "Orbit": Orbit,
        "LaunchSite": LaunchSite, "Outcome": Outcome, "Flights": Flights,
        "GridFins": GridFins, "Reused": Reused, "Legs": Legs, "LandingPad": LandingPad,
        "Block": Block, "ReusedCount": ReusedCount, "Serial": Serial,
        "Longitude": Longitude, "Latitude": Latitude,
    }
    df = pd.DataFrame(launch_dict)

    # Chỉ Falcon 9, đánh lại FlightNumber, thay PayloadMass thiếu bằng mean
    df = df[df["BoosterVersion"] != "Falcon 1"].reset_index(drop=True)
    df["FlightNumber"] = list(range(1, df.shape[0] + 1))
    df["PayloadMass"] = df["PayloadMass"].fillna(df["PayloadMass"].mean())

    df.to_csv("dataset_part_1.csv", index=False)
    print(df.shape); print(df.head())


if __name__ == "__main__":
    main()
