import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

def fetch_humidity_data(start_date, end_date):
    c = cdsapi.Client()
    grib_filename = "humidity_data.grib"
    temp_csv = "temp_data_humidity.csv"
    
    time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    
    if not os.path.exists(grib_filename):
        print("Mengunduh data dari Copernicus API...")
        
        try:
            c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "variable": "2m_dewpoint_temperature",
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

    if "d2m" in df.columns:
        df["d2m"] = df["d2m"] - 273.15
    else:
        raise KeyError("Kolom kelembapan 'd2m' tidak ditemukan dalam dataset!")

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    else:
        raise KeyError("Kolom waktu tidak ditemukan dalam dataset!")

    df["date"] = df["time"].dt.date
    df_daily_mean = df.groupby("date")["d2m"].mean().reset_index()
    df_daily_mean.rename(columns={"d2m": "mean_dewpoint_temperature"}, inplace=True)

        # Cek apakah file sudah ada dan baca datanya
        # **Perbaikan logika penyimpanan data**
    if os.path.exists(temp_csv):
        existing_data = pd.read_csv(temp_csv)
        new_data = df_daily_mean[~df_daily_mean["date"].astype(str).isin(existing_data["date"].astype(str))]
        if not new_data.empty:
            new_data.to_csv(temp_csv, mode='a', header=False, index=False)
            print(f"Data baru kelembapan disimpan ke {temp_csv}")
        else:
            print("Tidak ada data kelembapan baru untuk disimpan.")
    else:
        df_daily_mean.to_csv(temp_csv, mode='w', header=True, index=False)
        print(f"File {temp_csv} tidak ditemukan, membuat file baru dan menyimpan data.")

start_date = "2025-02-02"
end_date = datetime.today().strftime("%Y-%m-%d")
fetch_humidity_data(start_date, end_date)
