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
        "variable": "2m_dewpoint_temperature",
        "product_type": "reanalysis",
        "date": f"{start_date}/{end_date}",
        "time": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
        "format": "netcdf",
        "area": [-6.8, 112.5, -7.3, 113.0],  # [North, West, South, East] -> Bangkalan
    },
    "dewpoint_data.nc",
)

# Buka file NetCDF dan konversi ke DataFrame
ds = xr.open_dataset("dewpoint_data.nc")

# Pastikan time bukan indeks
df = ds.to_dataframe().reset_index()

# Cek apakah 'time' ada di kolom, kalau tidak cari kolom yang mengandung waktu
print(df.head())  # Cek isi dataframe
print(df.columns)  # Cek nama kolom yang ada

# Jika 'time' tidak ada, cari kolom yang berisi waktu, biasanya 'valid_time'
if 'time' not in df.columns:
    if 'valid_time' in df.columns:
        df.rename(columns={'valid_time': 'time'}, inplace=True)
    elif 'forecast_time' in df.columns:
        df.rename(columns={'forecast_time': 'time'}, inplace=True)
    else:
        raise KeyError("Kolom waktu tidak ditemukan dalam dataset!")

# Konversi waktu ke datetime
df["time"] = pd.to_datetime(df["time"])

# Konversi suhu dari Kelvin ke Celsius
df["d2m"] = df["d2m"] - 273.15  # d2m = 2m dewpoint temperature

# Hitung rata-rata harian
daily_mean = df.groupby(df["time"].dt.date)["d2m"].mean().reset_index()
daily_mean.rename(columns={"time": "date", "d2m": "mean_dewpoint_temperature"}, inplace=True)

# Simpan hasil ke CSV
daily_mean.to_csv("mean_dewpoint_bangkalan.csv", index=False)

print("Data berhasil disimpan ke mean_dewpoint_bangkalan.csv")
