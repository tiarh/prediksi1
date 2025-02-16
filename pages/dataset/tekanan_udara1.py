import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

# Inisialisasi client API
c = cdsapi.Client()

# Tentukan tanggal awal dan akhir
start_date = "2025-02-02"
end_date = datetime.today().strftime("%Y-%m-%d")

# Nama file sementara dan final
temp_filename = "temp_data.csv"
combined_filename = "combined_data.csv"
nc_filename = "pressure_data.nc"

# Cek apakah file sudah ada, jika tidak, download dari API
if not os.path.exists(nc_filename):
    print("Mengunduh data tekanan udara dari Copernicus API...")
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
        nc_filename,
    )
else:
    print(f"File {nc_filename} sudah ada, menggunakan file yang ada.")

# Buka file NetCDF
ds = xr.open_dataset(nc_filename)
df = ds.to_dataframe().reset_index()

# Konversi waktu
if "time" in df.columns:
    df["time"] = pd.to_datetime(df["time"])
else:
    raise KeyError("Kolom waktu tidak ditemukan dalam dataset!")

# Konversi tekanan dari Pascal ke hPa
df["sp"] = df["sp"] / 100  # sp = surface pressure

# Hitung rata-rata harian
df["date"] = df["time"].dt.date
daily_mean = df.groupby("date")["sp"].mean().reset_index()
daily_mean.rename(columns={"sp": "mean_surface_pressure_hPa"}, inplace=True)

# Simpan ke file sementara
daily_mean.to_csv(temp_filename, mode='a', header=not os.path.exists(temp_filename), index=False)

# Cek apakah ada tanggal yang sudah muncul 5 kali
if os.path.exists(temp_filename):
    temp_df = pd.read_csv(temp_filename)
    date_counts = temp_df["date"].value_counts()
    valid_dates = date_counts[date_counts >= 5].index.tolist()
    
    if valid_dates:
        # Ambil data dengan tanggal yang sudah 5 kali
        data_to_move = temp_df[temp_df["date"].isin(valid_dates)]
        
        # Simpan ke file combined
        data_to_move.to_csv(combined_filename, mode='a', header=not os.path.exists(combined_filename), index=False)
        
        # Hapus data yang sudah dipindahkan dari temp
        temp_df = temp_df[~temp_df["date"].isin(valid_dates)]
        temp_df.to_csv(temp_filename, index=False)

print(f"Data tekanan udara diproses dan disimpan sementara ke {temp_filename}")
