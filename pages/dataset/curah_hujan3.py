import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

def fetch_precipitation_data(start_date, end_date):
    c = cdsapi.Client()
    grib_filename = "precipitation.grib"
    temp_csv = "temp_data_precipitation.csv"
    
    time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    
    if not os.path.exists(grib_filename):
        print("Mengunduh data curah hujan dari Copernicus API...")
        
        try:
            c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "variable": "total_precipitation",
                    "product_type": ["reanalysis"],
                    "data_format": "grib",
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

    df["date"] = pd.to_datetime(df["time"]).dt.date
    df_daily_mean = df.groupby("date")["tp"].mean().reset_index()
    
    df_daily_mean.to_csv(temp_csv, mode='a', header=not os.path.exists(temp_csv), index=False)
    print(f"Data curah hujan sementara disimpan ke {temp_csv}")

# Contoh pemanggilan
start_date = "2025-02-02"
end_date = datetime.today().strftime("%Y-%m-%d")
fetch_precipitation_data(start_date, end_date)
