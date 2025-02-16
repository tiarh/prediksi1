import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

def fetch_precipitation(start_date, end_date):
    c = cdsapi.Client()
    nc_filename = "precipitation.nc"
    temp_filename = "temp_data.csv"
    combined_filename = "combined_data.csv"
    
    # Unduh data jika belum ada
    if not os.path.exists(nc_filename):
        print("Mengunduh data curah hujan dari Copernicus API...")
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "variable": "total_precipitation",
                "product_type": "reanalysis",
                "date": f"{start_date}/{end_date}",
                "time": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
                "format": "netcdf",
                "area": [-6.8, 112.5, -7.3, 113.0],
            },
            nc_filename,
        )
    
    # Buka file NetCDF
    ds = xr.open_dataset(nc_filename)
    ds["tp"] = ds["tp"] * 1000  # Konversi ke mm
    df = ds.to_dataframe().reset_index()
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date  # Ambil tanggal saja
    df_daily_mean = df.groupby("date")["tp"].mean().reset_index()
    df_daily_mean.rename(columns={"tp": "precipitation"}, inplace=True)
    
    # Simpan ke temp file
    df_daily_mean.to_csv(temp_filename, index=False, mode='a', header=not os.path.exists(temp_filename))
    print(f"Data sementara disimpan ke {temp_filename}")
    
    # Cek apakah sudah ada 5 data dari tanggal yang sama
    temp_df = pd.read_csv(temp_filename)
    grouped = temp_df.groupby("date").size()
    
    for date, count in grouped.items():
        if count >= 5:
            print(f"Memindahkan data tanggal {date} ke {combined_filename}")
            selected_data = temp_df[temp_df["date"] == date]
            selected_data.to_csv(combined_filename, index=False, mode='a', header=not os.path.exists(combined_filename))
            temp_df = temp_df[temp_df["date"] != date]
    
    # Simpan ulang temp tanpa data yang sudah dipindah
    temp_df.to_csv(temp_filename, index=False)
    print("Proses selesai!")

# Jalankan dengan start 2 Februari 2025
fetch_precipitation("2025-02-02", datetime.today().strftime("%Y-%m-%d"))
