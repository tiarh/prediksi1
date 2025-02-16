import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

# Inisialisasi client API
c = cdsapi.Client()

# Tentukan tanggal awal dan akhir
start_date = "2019-08-01"
end_date = datetime.today().strftime("%Y-%m-%d")

# Nama file hasil download
nc_filename = "precipitation.nc"
csv_filename = "daily_mean_precipitation_bangkalan.csv"

# Cek apakah file sudah ada, jika tidak, download dari API
if not os.path.exists(nc_filename):
    print("Mengunduh data curah hujan dari Copernicus API...")
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": "total_precipitation",
            "product_type": "reanalysis",
            "date": f"{start_date}/{end_date}",
            "time": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],  # Setiap 3 jam
            "format": "netcdf",
            "area": [-6.8, 112.5, -7.3, 113.0],  # [North, West, South, East] -> Bangkalan
        },
        nc_filename,
    )
else:
    print(f"File {nc_filename} sudah ada, menggunakan file yang ada.")

# Buka file NetCDF
ds = xr.open_dataset(nc_filename)

# Konversi curah hujan dari meter ke milimeter (m -> mm)
ds["tp"] = ds["tp"] * 1000  # 1 meter = 1000 mm

# Konversi dataset ke DataFrame
df = ds.to_dataframe().reset_index()

# Pastikan kolom waktu ada
time_col = "time" if "time" in df.columns else df.columns[df.columns.str.contains("time")][0]

# Ubah format waktu
df[time_col] = pd.to_datetime(df[time_col])

# Hitung rata-rata curah hujan harian dari 8 data (tiap 3 jam)
df["date"] = df[time_col].dt.date  # Ambil tanggal saja
df_daily_mean_precip = df.groupby("date")["tp"].mean().reset_index()

# Simpan ke CSV
df_daily_mean_precip.to_csv(csv_filename, index=False)

print(f"Data rata-rata curah hujan harian disimpan ke {csv_filename}")
