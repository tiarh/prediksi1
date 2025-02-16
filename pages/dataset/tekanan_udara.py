import cdsapi
import xarray as xr
import pandas as pd
from datetime import datetime

# Inisialisasi client API
c = cdsapi.Client()

# Tentukan tanggal awal dan akhir
start_date = "2019-08-01"
end_date = datetime.today().strftime("%Y-%m-%d")

# Request data setiap 3 jam
c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "variable": "surface_pressure",
        "product_type": "reanalysis",
        "date": f"{start_date}/{end_date}",
        "time": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
        "format": "netcdf",
        "area": [-6.8, 112.5, -7.3, 113.0],  # [North, West, South, East] -> Bangkalan
    },
    "pressure_data.nc",
)

# Buka file NetCDF dan konversi ke DataFrame
ds = xr.open_dataset("pressure_data.nc")
df = ds.to_dataframe().reset_index()

# Cek kolom yang tersedia
print(df.head())
print(df.columns)

# Rename kolom waktu jika perlu
if 'time' not in df.columns:
    if 'valid_time' in df.columns:
        df.rename(columns={'valid_time': 'time'}, inplace=True)
    elif 'forecast_time' in df.columns:
        df.rename(columns={'forecast_time': 'time'}, inplace=True)
    else:
        raise KeyError("Kolom waktu tidak ditemukan dalam dataset!")

# Konversi waktu ke datetime
df["time"] = pd.to_datetime(df["time"])

# Konversi tekanan dari Pascal ke hPa (hectopascal)
df["sp"] = df["sp"] / 100  # sp = surface pressure

# Hitung rata-rata harian
daily_mean = df.groupby(df["time"].dt.date)["sp"].mean().reset_index()
daily_mean.rename(columns={"time": "date", "sp": "mean_surface_pressure_hPa"}, inplace=True)

# Simpan hasil ke CSV
daily_mean.to_csv("mean_surface_pressure_bangkalan.csv", index=False)

print("Data berhasil disimpan ke mean_surface_pressure_bangkalan.csv")
