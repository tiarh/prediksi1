import pandas as pd
import numpy as np
import os

# Path file gabungan
combined_file = '/root/prediksi/pages/dataset/combined_data.csv'

# Load datasets sementara
df_beras = pd.read_csv('/root/prediksi/pages/dataset/temp_data1.csv')
df_suhu = pd.read_csv('/root/prediksi/pages/dataset/temp_data_suhu.csv')
df_hujan = pd.read_csv('/root/prediksi/pages/dataset/temp_data_precipitation.csv')
df_udara = pd.read_csv('/root/prediksi/pages/dataset/temp_data_pressure.csv')
df_kelembapan = pd.read_csv('/root/prediksi/pages/dataset/temp_data_humidity.csv')

# Bersihkan data harga beras (hapus 'Rp. ' dan ',')
df_beras['Price'] = df_beras['Price'].replace({'Rp. ': '', ',': ''}, regex=True).astype(float)

# Konversi tanggal
df_beras['Date'] = pd.to_datetime(df_beras['Date'], errors='coerce')
df_suhu['date'] = pd.to_datetime(df_suhu['date'], errors='coerce')
df_hujan['date'] = pd.to_datetime(df_hujan['date'], errors='coerce')
df_udara['date'] = pd.to_datetime(df_udara['date'], errors='coerce')
df_kelembapan['date'] = pd.to_datetime(df_kelembapan['date'], errors='coerce')

# Hapus baris dengan tanggal yang tidak valid
df_beras.dropna(subset=['Date'], inplace=True)
df_suhu.dropna(subset=['date'], inplace=True)
df_hujan.dropna(subset=['date'], inplace=True)
df_udara.dropna(subset=['date'], inplace=True)
df_kelembapan.dropna(subset=['date'], inplace=True)

# Cari tanggal terbaru yang tersedia di semua dataset
min_common_date = min(df_beras['Date'].max(), df_suhu['date'].max(), df_hujan['date'].max(),
                      df_udara['date'].max(), df_kelembapan['date'].max())

# Filter data hingga tanggal yang tersedia di semua dataset
df_beras = df_beras[df_beras['Date'] <= min_common_date]
df_suhu = df_suhu[df_suhu['date'] <= min_common_date]
df_hujan = df_hujan[df_hujan['date'] <= min_common_date]
df_udara = df_udara[df_udara['date'] <= min_common_date]
df_kelembapan = df_kelembapan[df_kelembapan['date'] <= min_common_date]

# Gabungkan data berdasarkan tanggal
df_combined = pd.merge(df_beras, df_suhu[['date', 't2m']], left_on='Date', right_on='date', how='left')
df_combined = pd.merge(df_combined, df_kelembapan[['date', 'mean_dewpoint_temperature']], on='date', how='left')
df_combined = pd.merge(df_combined, df_hujan[['date', 'tp']], on='date', how='left')
df_combined = pd.merge(df_combined, df_udara[['date', 'mean_surface_pressure_hPa']], on='date', how='left')

# Hapus kolom 'date' yang duplikat
df_combined.drop(columns=['date'], inplace=True)

# Jika file gabungan sudah ada, cek tanggal yang sudah ada
if os.path.exists(combined_file):
    existing_data = pd.read_csv(combined_file)
    existing_dates = set(pd.to_datetime(existing_data['Date']).dt.date.astype(str))
    
    # Hanya ambil data dengan tanggal yang belum ada di file gabungan
    df_combined = df_combined[~df_combined['Date'].astype(str).isin(existing_dates)]
    
    if not df_combined.empty:
        df_combined.to_csv(combined_file, mode='a', header=False, index=False)
        print(f"Data baru berhasil ditambahkan ke {combined_file}!")
    else:
        print("Tidak ada data baru untuk ditambahkan.")
else:
    df_combined.to_csv(combined_file, index=False)
    print(f"File {combined_file} berhasil dibuat dan data pertama dimasukkan!")
