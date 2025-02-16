import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

# Inisialisasi client API
c = cdsapi.Client()

# Tentukan tanggal awal (2 Februari 2025) dan akhir (hari ini)
start_date = "2025-02-02"
end_date = datetime.today().strftime("%Y-%m-%d")

# Nama file hasil download
nc_filename = "temperature_data.nc"
temp_csv = "temp_data.csv"
combined_csv = "combined_data.csv"

# Jam pengambilan data (tiap 3 jam)
time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]

# Download data jika belum ada
if not os.path.exists(nc_filename):
    print("Mengunduh data dari Copernicus API...")
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": "2m_temperature",
            "product_type": "reanalysis",
            "date": f"{start_date}/{end_date}",
            "time": time_intervals,
            "format": "netcdf",
            "area": [-6.8, 112.5, -7.3, 113.0],  # [North, West, South, East] -> Bangkalan
        },
        nc_filename,
    )
else:
    print(f"File {nc_filename} sudah ada, menggunakan file yang ada.")

# Buka file NetCDF
ds = xr.open_dataset(nc_filename)

# Konversi suhu dari Kelvin ke Celsius
ds["t2m"] = ds["t2m"] - 273.15

# Konversi dataset ke DataFrame
df = ds.to_dataframe().reset_index()

time_col = "time"
df[time_col] = pd.to_datetime(df[time_col])

df["date"] = df[time_col].dt.date  # Ambil tanggal saja
df_daily_mean = df.groupby("date")["t2m"].mean().reset_index()

# Simpan ke temp_data.csv (sementara)
if os.path.exists(temp_csv):
    df_temp = pd.read_csv(temp_csv)
    df_combined = pd.concat([df_temp, df_daily_mean])
else:
    df_combined = df_daily_mean

df_combined.to_csv(temp_csv, index=False)
print(f"Data suhu rata-rata harian disimpan sementara di {temp_csv}")

# Cek apakah ada 5 data dengan tanggal yang sama
df_temp = pd.read_csv(temp_csv)
if df_temp.groupby("date").size().max() >= 5:
    df_temp.to_csv(combined_csv, mode='a', header=not os.path.exists(combined_csv), index=False)
    df_temp = df_temp.groupby("date").filter(lambda x: len(x) < 5)
    df_temp.to_csv(temp_csv, index=False)
    print(f"Data dipindahkan ke {combined_csv}")
