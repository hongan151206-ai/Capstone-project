"""3. Data Wrangling - tạo nhãn Class (1 = landing thành công)  ->  dataset_part_2.csv"""
import pandas as pd

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_1.csv")


def main():
    try:
        df = pd.read_csv("dataset_part_1.csv")
    except FileNotFoundError:
        df = pd.read_csv(URL)

    print("Missing %:\n", df.isnull().sum() / len(df) * 100)
    print("\nLaunches per site:\n", df["LaunchSite"].value_counts())
    print("\nOrbits:\n", df["Orbit"].value_counts())

    landing_outcomes = df["Outcome"].value_counts()
    print("\nOutcomes:\n", landing_outcomes)

    bad_outcomes = {"False Ocean", "False RTLS", "False ASDS", "None ASDS", "None None"}
    df["Class"] = df["Outcome"].apply(lambda x: 0 if x in bad_outcomes else 1)
    print("\nSuccess rate:", df["Class"].mean())

    df.to_csv("dataset_part_2.csv", index=False)


if __name__ == "__main__":
    main()
