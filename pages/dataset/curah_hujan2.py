import cdsapi
import pandas as pd
import os
from datetime import datetime

# Inisialisasi client API
c = cdsapi.Client()

# Tentukan tanggal awal (2 Februari 2025) dan akhir (hari ini)
start_date = "2025-02-02"
end_date = datetime.today().strftime("%Y-%m-%d")

# Nama file hasil download
grib_filename = "precipitation.grib"
temp_csv = "temp_data.csv"
combined_csv = "combined_data.csv"

# Jam pengambilan data (tiap 3 jam)
time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]

# Download data jika belum ada
if not os.path.exists(grib_filename):
    print("Mengunduh data curah hujan dari Copernicus API...")
    
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": ["total_precipitation"],
            "product_type": ["reanalysis"],
            "date": f"{start_date}/{end_date}",
            "time": time_intervals,
            "data_format": "grib",
            "download_format": "unarchived",
            "area": [-6.8, 112.5, -7.3, 113.0],  # [North, West, South, East] -> Bangkalan
        },
        grib_filename,
    )
else:
    print(f"File {grib_filename} sudah ada, menggunakan file yang ada.")

# Convert GRIB ke CSV menggunakan Pandas
df = pd.read_csv(grib_filename)
df["time"] = pd.to_datetime(df["time"])
df["date"] = df["time"].dt.date  # Ambil tanggal saja

# Hitung rata-rata harian
df_daily_mean = df.groupby("date")["total_precipitation"].mean().reset_index()
df_daily_mean.rename(columns={"total_precipitation": "precipitation_mm"}, inplace=True)

# Simpan ke temp_data.csv (sementara)
df_daily_mean.to_csv(temp_csv, mode='a', header=not os.path.exists(temp_csv), index=False)
print(f"Data curah hujan rata-rata harian disimpan sementara di {temp_csv}")

# Cek apakah ada 5 data dengan tanggal yang sama
df_temp = pd.read_csv(temp_csv)
if df_temp.groupby("date").size().max() >= 5:
    df_temp.to_csv(combined_csv, mode='a', header=not os.path.exists(combined_csv), index=False)
    df_temp = df_temp.groupby("date").filter(lambda x: len(x) < 5)
    df_temp.to_csv(temp_csv, index=False)
    print(f"Data dipindahkan ke {combined_csv}")
