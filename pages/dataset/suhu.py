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
nc_filename = "temperature_data.nc"
csv_filename = "mean_temperature_bangkalan.csv"

# Jam pengambilan data (tiap 3 jam)
time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]

# Cek apakah file sudah ada, jika tidak, download dari API
if not os.path.exists(nc_filename):
    print("Mengunduh data dari Copernicus API...")
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": "2m_temperature",
            "product_type": "reanalysis",
            "date": f"{start_date}/{end_date}",
            "time": time_intervals,  # Ambil data tiap 3 jam
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

# Pastikan kolom waktu ada
time_col = "time" if "time" in df.columns else df.columns[df.columns.str.contains("time")][0]

# Ubah format waktu
df[time_col] = pd.to_datetime(df[time_col])

# Hitung rata-rata suhu harian
df["date"] = df[time_col].dt.date  # Ambil tanggal saja
df_daily_mean = df.groupby("date")["t2m"].mean().reset_index()

# Simpan ke CSV
df_daily_mean.to_csv(csv_filename, index=False)

print(f"Data suhu rata-rata harian disimpan ke {csv_filename}")
