import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

def fetch_temperature_data(start_date, end_date):
    c = cdsapi.Client()
    grib_filename = "temperature_data.grib"
    temp_csv = "temp_data.csv"
    combined_csv = "combined_data.csv"
    
    time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    
    if not os.path.exists(grib_filename):
        print("Mengunduh data dari Copernicus API...")
        
        try:
            c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "variable": "2m_temperature",
                    "product_type": ["reanalysis"],
                    "data_format": "grib",  # Format API terbaru
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

    # Buka file GRIB menggunakan cfgrib
    try:
        ds = xr.open_dataset(grib_filename, engine="cfgrib")
        df = ds.to_dataframe().reset_index()
    except Exception as e:
        print(f"Error membaca file GRIB: {e}")
        return

    # Konversi suhu dari Kelvin ke Celsius
    if "t2m" in df.columns:
        df["t2m"] = df["t2m"] - 273.15
    else:
        raise KeyError("Kolom suhu 't2m' tidak ditemukan dalam dataset!")

    # Konversi waktu
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    else:
        raise KeyError("Kolom waktu tidak ditemukan dalam dataset!")

    df["date"] = df["time"].dt.date
    df_daily_mean = df.groupby("date")["t2m"].mean().reset_index()
    df_daily_mean.rename(columns={"t2m": "mean_temperature_C"}, inplace=True)

    # Simpan ke file sementara
    df_daily_mean.to_csv(temp_csv, mode='a', header=not os.path.exists(temp_csv), index=False)
    print(f"Data suhu sementara disimpan ke {temp_csv}")

    # Cek apakah ada tanggal yang sudah muncul 5 kali
    if os.path.exists(temp_csv):
        temp_data = pd.read_csv(temp_csv)
        date_counts = temp_data["date"].value_counts()
        valid_dates = date_counts[date_counts >= 5].index.tolist()

        if valid_dates:
            # Pindahkan data yang sudah cukup ke file final
            combined_data = temp_data[temp_data["date"].isin(valid_dates)]
            
            # Simpan ke file combined
            combined_data.to_csv(combined_csv, mode='a', header=not os.path.exists(combined_csv), index=False)
            
            # Hapus data yang sudah dipindahkan dari temp
            temp_data = temp_data[~temp_data["date"].isin(valid_dates)]
            temp_data.to_csv(temp_csv, index=False)
            
            print(f"{len(valid_dates)} tanggal dipindahkan ke {combined_csv}")
            print("Data sementara diperbarui.")

fetch_temperature_data("2025-02-02", datetime.today().strftime("%Y-%m-%d"))
