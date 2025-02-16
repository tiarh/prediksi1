import xarray as xr

# Buka file NetCDF
ds = xr.open_dataset("dewpoint_data.nc")

# Tampilkan struktur dataset
print(ds)
