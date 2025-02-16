import cdsapi
import xarray as xr
import pandas as pd
import os
from datetime import datetime

def fetch_temperature_data(start_date, end_date):
    c = cdsapi.Client()
    nc_filename = "temperature_data.nc"
    temp_csv = "temp_data.csv"
    combined_csv = "combined_data.csv"
    
    time_intervals = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    
    if not os.path.exists(nc_filename):
        print("Mengunduh data dari Copernicus API...")
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "variable": "2m_temperature",
                "product_type": "reanalysis",
                "date": f"{start_date}/{end_date}",
                "time": time_intervals,
                "format": "netcdf",
                "area": [-6.8, 112.5, -7.3, 113.0],
            },
            nc_filename,
        )
    else:
        print(f"File {nc_filename} sudah ada, menggunakan file yang ada.")
    
    ds = xr.open_dataset(nc_filename)
    ds["t2m"] = ds["t2m"] - 273.15  # Kelvin ke Celsius
    df = ds.to_dataframe().reset_index()
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    df_daily_mean = df.groupby("date")["t2m"].mean().reset_index()
    
    if os.path.exists(temp_csv):
        existing_data = pd.read_csv(temp_csv)
        df_daily_mean = pd.concat([existing_data, df_daily_mean])
    
    df_daily_mean.to_csv(temp_csv, index=False)
    print(f"Data suhu sementara disimpan ke {temp_csv}")
    
    temp_data = pd.read_csv(temp_csv)
    count_per_date = temp_data["date"].value_counts()
    valid_dates = count_per_date[count_per_date >= 5].index
    
    if len(valid_dates) > 0:
        combined_data = temp_data[temp_data["date"].isin(valid_dates)]
        
        if os.path.exists(combined_csv):
            combined_existing = pd.read_csv(combined_csv)
            combined_data = pd.concat([combined_existing, combined_data])
        
        combined_data.to_csv(combined_csv, index=False)
        print(f"{len(valid_dates)} tanggal dipindahkan ke {combined_csv}")
        temp_data = temp_data[~temp_data["date"].isin(valid_dates)]
        temp_data.to_csv(temp_csv, index=False)
        print("Data sementara diperbarui.")
    
fetch_temperature_data("2025-02-02", datetime.today().strftime("%Y-%m-%d"))
