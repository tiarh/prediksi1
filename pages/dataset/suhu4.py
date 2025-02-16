import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

def fetch_temperature_data(start_date, end_date):
    c = cdsapi.Client()
    grib_filename = "temperature_data.grib"
    temp_csv = "temp_data_suhu.csv"
    
    time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    
    if not os.path.exists(grib_filename):
        print("Mengunduh data dari Copernicus API...")
        
        try:
            c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "variable": "2m_temperature",
                    "product_type": ["reanalysis"],
                    "data_format": "grib",
                    "download_format": "unarchived",
                    "date": f"{start_date}/{end_date}",
                    "time": time_intervals,
                    "area": [-6.8, 112.5, -7.3, 113.0],  # Bangkalan
                }
            ).download(grib_filename)
            print("Download selesai.")
        except Exception as e:
            print(f"Error saat mengunduh data: {e}")
            return
    else:
        print(f"File {grib_filename} sudah ada, menggunakan file yang ada.")

    try:
        ds = xr.open_dataset(grib_filename, engine="cfgrib")
        df = ds.to_dataframe().reset_index()
    except Exception as e:
        print(f"Error membaca file GRIB: {e}")
        return

    if "t2m" in df.columns:
        df["t2m"] = df["t2m"] - 273.15
    else:
        raise KeyError("Kolom suhu 't2m' tidak ditemukan dalam dataset!")

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    else:
        raise KeyError("Kolom waktu tidak ditemukan dalam dataset!")

    df["date"] = df["time"].dt.date
    df_daily_mean = df.groupby("date")["t2m"].mean().reset_index()
    
    # Cek apakah file sudah ada dan baca datanya
    if os.path.exists(temp_csv):
        existing_df = pd.read_csv(temp_csv)
        existing_dates = set(existing_df["date"].astype(str))
        df_daily_mean = df_daily_mean[~df_daily_mean["date"].astype(str).isin(existing_dates)]
    
    # Simpan hanya data yang belum ada
    if not df_daily_mean.empty:
        df_daily_mean.to_csv(temp_csv, mode='a', header=not os.path.exists(temp_csv), index=False)
        print(f"Data suhu baru disimpan ke {temp_csv}")
    else:
        print("Tidak ada data suhu baru untuk disimpan.")

fetch_temperature_data("2025-02-02", datetime.today().strftime("%Y-%m-%d"))
