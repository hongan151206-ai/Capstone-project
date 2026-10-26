"""Chạy toàn bộ pipeline rồi dựng slide PDF.  python run_all.py   (cần Internet, ~vài phút do GridSearchCV)"""
import subprocess
import sys

STEPS = ["01_spacex_api_collection.py", "02_web_scraping.py", "03_data_wrangling.py", "04_eda_sql.py",
         "05_eda_visualization.py", "06_folium_map.py", "07b_dash_figures.py", "08_predictive_analysis.py",
         "build_report.py"]

for s in STEPS:
    print(f"\n########## {s}")
    r = subprocess.run([sys.executable, s])
    if r.returncode != 0:
        print(f"!! {s} lỗi (mã {r.returncode}) - kiểm tra mạng/đường dẫn rồi chạy lại từ bước này")
        if s in ("03_data_wrangling.py", "05_eda_visualization.py", "08_predictive_analysis.py"):
            sys.exit(r.returncode)   # các bước cốt lõi; còn lại có thể bỏ qua
