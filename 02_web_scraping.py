"""2. Data Collection - Web scraping Wikipedia (Falcon 9 launches)  ->  spacex_web_scraped.csv"""
import re
import unicodedata
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = ("https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches"
       "&oldid=1027686922")


def date_time(cell):
    return [t.strip() for t in list(cell.strings)][0:2]


def booster_version(cell):
    return "".join([b for i, b in enumerate(cell.strings) if i % 2 == 0][0:-1])


def landing_status(cell):
    return [i for i in cell.strings][0]


def get_mass(cell):
    mass = unicodedata.normalize("NFKD", cell.text).strip()
    if mass:
        mass = mass[:mass.find("kg") + 2]
        return mass
    return 0


def extract_column_from_header(row):
    if row.br:
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()
    name = " ".join(row.contents).strip() if all(isinstance(c, str) for c in row.contents) \
        else row.get_text(" ", strip=True)
    return None if (name.isdigit() or not name) else name


def main():
    soup = BeautifulSoup(requests.get(URL, timeout=60).text, "html.parser")
    html_tables = soup.find_all("table")
    first_launch_table = html_tables[2]

    column_names = []
    for th in first_launch_table.find_all("th"):
        n = extract_column_from_header(th)
        if n:
            column_names.append(n)

    launch_dict = {k: [] for k in
                   ["Flight No.", "Launch site", "Payload", "Payload mass", "Orbit", "Customer",
                    "Launch outcome", "Version Booster", "Booster landing", "Date", "Time"]}

    for table in soup.find_all("table", "wikitable plainrowheaders collapsible"):
        for rows in table.find_all("tr"):
            flight_cell = rows.th
            if flight_cell and flight_cell.string and flight_cell.string.strip().isdigit():
                flight_number = flight_cell.string.strip()
            else:
                flight_number = None
            row = rows.find_all("td")
            if flight_number is None or len(row) < 9:
                continue
            d, t = date_time(row[0])
            launch_dict["Flight No."].append(flight_number)
            launch_dict["Date"].append(d.strip(","))
            launch_dict["Time"].append(t)
            launch_dict["Version Booster"].append(booster_version(row[1]) or row[1].a.string)
            launch_dict["Launch site"].append(row[2].a.string)
            launch_dict["Payload"].append(row[3].a.string)
            launch_dict["Payload mass"].append(get_mass(row[4]))
            launch_dict["Orbit"].append(row[5].a.string)
            launch_dict["Customer"].append(row[6].a.string if row[6].a else row[6].text.strip())
            launch_dict["Launch outcome"].append(list(row[7].strings)[0])
            launch_dict["Booster landing"].append(landing_status(row[8]))

    df = pd.DataFrame(launch_dict)
    df.to_csv("spacex_web_scraped.csv", index=False)
    print(df.shape); print(df.head())


if __name__ == "__main__":
    main()
