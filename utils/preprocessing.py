import pandas as pd
import numpy as np
import streamlit as st
from sklearn.preprocessing import MinMaxScaler


@st.cache_data
def load_data():
    try:
        # Batasi jumlah baris untuk mencegah kehabisan RAM
        max_rows = 100000  

        # Fungsi untuk membaca CSV tanpa konversi float
        def read_csv_optimized(url, nrows=max_rows):
            return pd.read_csv(url, encoding="utf-8", on_bad_lines="skip", nrows=nrows)

        # Muat data tanpa konversi tipe
        beras = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/data_Bangkalan_beras_quality_medium_1.csv")
        suhu = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Temperature_2019_2024%20new.csv")
        hujan = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Rainfall_2019_2024.csv")
        udara = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Pressure_2019_2024%203%20f.csv")
        kelembapan = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Dew_Point_Daily_2019_2024c.csv")

        print("✅ Berhasil memuat semua data tanpa konversi.")

        return {"beras": beras, "suhu": suhu, "hujan": hujan, "udara": udara, "kelembapan": kelembapan}

    except Exception as e:
        st.error(f"❌ Error memuat atau memproses data: {e}")
        return None


# Fungsi untuk mengecek missing value
def cek_missing_value(df, nama_df):
    missing_count = df.isnull().sum().sum()
    st.write(f"🔍 Missing values untuk {nama_df}: {missing_count} data")
    if missing_count > 0:
        st.write(df.isnull().sum())

# Fungsi preprocessing data
def preprocessing(df_beras, df_suhu, df_hujan, df_udara, df_kelembapan, n_steps_in):
    # Batasi jumlah data yang diproses
    max_rows = 10000  # Sesuaikan dengan kapasitas RAM
    df_beras = df_beras.iloc[:max_rows]
    df_suhu = df_suhu.iloc[:max_rows]
    df_hujan = df_hujan.iloc[:max_rows]
    df_udara = df_udara.iloc[:max_rows]
    df_kelembapan = df_kelembapan.iloc[:max_rows]

    # Membersihkan kolom Price (untuk df_beras)
    df_beras.loc[:, 'Price'] = df_beras['Price'].replace({'Rp. ': '', ',': ''}, regex=True).astype(float)

    # Mengonversi kolom tanggal menjadi format datetime
    df_beras['Date'] = pd.to_datetime(df_beras['Date'], dayfirst=True, errors='coerce')
    df_suhu['date'] = pd.to_datetime(df_suhu['date'], dayfirst=True, errors='coerce')
    df_hujan['date'] = pd.to_datetime(df_hujan['date'], dayfirst=True, errors='coerce')
    df_udara['date'] = pd.to_datetime(df_udara['date'], dayfirst=True, errors='coerce')
    df_kelembapan['date'] = pd.to_datetime(df_kelembapan['date'], dayfirst=True, errors='coerce')

    # Gabungkan data berdasarkan tanggal
    df_combined = pd.merge(df_beras, df_suhu, left_on='Date', right_on='date', how='left')
    df_combined = pd.merge(df_combined, df_kelembapan, on='date', how='left')
    df_combined = pd.merge(df_combined, df_hujan, on='date', how='left')
    df_combined = pd.merge(df_combined, df_udara, on='date', how='left')

    # Hapus kolom 'date' yang duplikat
    df_combined = df_combined.drop(columns=['date'])

    # Tampilkan missing values setelah preprocessing
    cek_missing_value(df_combined, "df_combined")
    
    # Pilih fitur yang akan digunakan
    features = ['Price', 'temperature_celsius', 'dewpoint_Celsius', 'precipitation', 'mean_pressure']
    df = df_combined[features]

    # Konversi tipe data agar lebih hemat memori
    for col in df.columns:
        df[col] = df[col].astype('float32')

    # Fungsi untuk membuat dataset secara efisien dengan generator
    def create_dataset_generator(df, n_steps_in, n_steps_out):
        for i in range(len(df) - n_steps_in - n_steps_out + 1):
            X = df.iloc[i:i + n_steps_in].values
            y = df.iloc[i + n_steps_in:i + n_steps_in + n_steps_out]['Price'].values
            yield X, y

    # Konversi generator ke list untuk streamlit
    data_gen = list(create_dataset_generator(df, n_steps_in, 7))
    
    X = np.array([item[0] for item in data_gen])
    y = np.array([item[1] for item in data_gen])

    # Reshape X untuk membuat DataFrame
    n_samples, n_time_steps, n_features = X.shape
    X_flat = X.reshape(n_samples, n_time_steps * n_features)

    # Generate feature column names
    feature_columns = []
    for step in range(n_steps_in):
        feature_columns.extend([
            f'HB-{n_steps_in-step-1}',
            f'SH-{n_steps_in-step-1}',
            f'KL-{n_steps_in-step-1}',
            f'CH-{n_steps_in-step-1}',
            f'TU-{n_steps_in-step-1}'
        ])

    # Buat DataFrame untuk fitur
    X_df = pd.DataFrame(X_flat, columns=feature_columns)

    # Buat DataFrame untuk target
    y_df = pd.DataFrame(y, columns=[f'HB+{i+1}' for i in range(7)])

    # Gabungkan X dan y dalam satu DataFrame
    combined_df = pd.concat([X_df, y_df], axis=1)

    # Simpan ke CSV
    combined_csv_file = "combined_data.csv"
    combined_df.to_csv(combined_csv_file, index=False)

    # Tampilkan hasil preprocessing
    st.write("📊 **Hasil Preprocessing Data:**")
    st.write(combined_df.head())

    return combined_df

# Streamlit untuk tampilan
st.title("📂 Data Mentah dan Preprocessing")

# Tampilkan data mentah
st.subheader("📊 Data Mentah")
try:
    data = load_data()
    
    if not data:
        st.error("❌ Tidak ada data yang berhasil dimuat.")
        st.stop()

    for name, df in data.items():
        with st.expander(f"📄 Data {name.capitalize()}"):
            show_all = st.checkbox(f"Tampilkan semua data {name.capitalize()}", key=name)
            if show_all:
                st.dataframe(df)
            else:
                st.dataframe(df.head(10))

    # Pilih lag untuk preprocessing
    lag_options = [30, 60, 90]
    selected_lag = st.selectbox("⏳ Pilih Lag (steps in):", lag_options)

    # Tambahkan tombol untuk menjalankan preprocessing
    if st.button("🚀 Jalankan Preprocessing"):
        st.subheader("📂 Preprocessing")
        combined_df = preprocessing(data['beras'], data['suhu'], data['hujan'], data['udara'], data['kelembapan'], selected_lag)


except Exception as e:
    st.error(f"❌ Error saat memuat data: {e}")
    st.stop()
