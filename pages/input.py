import streamlit as st
import pandas as pd
from datetime import timedelta

# File path atau URL CSV
data_file = "/root/prediksi/pages/dataset/combined_data.csv"  # Sesuaikan dengan file Anda

# Fungsi untuk membaca data dari CSV
@st.cache_data
def load_data():
    data = pd.read_csv(data_file)
    data["Date"] = pd.to_datetime(data["Date"]).dt.date  # Hapus jam dari kolom Date
    return data

# Load data awal ke session state
if "data" not in st.session_state:
    st.session_state["data"] = load_data()

# Judul halaman
st.title("Input Data")
st.write("Halaman ini digunakan untuk input parameter prediksi.")

# Tampilkan data saat ini
st.subheader("📊 Data Saat Ini")
st.dataframe(st.session_state["data"])  # Tampilkan semua data

# Tampilkan tanggal data terbaru
latest_date = st.session_state["data"]["Date"].max()
st.write(f"🕒 **Latest Data Update:** {latest_date}")

# Input untuk data baru
st.subheader("📝 Input Parameter Prediksi")
HB = st.number_input("HB (Harga Beras)", min_value=0.0, format="%.2f")
SH = st.number_input("SH (Suhu)", min_value=-50.0, max_value=50.0, format="%.2f")
KL = st.number_input("KL (Kelembapan)", min_value=0.0, max_value=100.0, format="%.2f")
CH = st.number_input("CH (Curah Hujan)", min_value=0.0, format="%.2f")
TU = st.number_input("TU (Tekanan Udara)", min_value=0.0, format="%.2f")

# Tombol Simpan
if st.button("Simpan"):
    try:
        # Data baru
        last_date = st.session_state["data"]["Date"].iloc[-1]
        new_date = last_date + timedelta(days=1)
        new_row = pd.DataFrame({
            "Date": [new_date],
            "Kabupaten": ["Bangkalan"],
            "Price": [HB],
            "temperature_celsius": [SH],
            "dewpoint_Celsius": [KL],
            "precipitation": [CH],
            "mean_pressure": [TU]
        })

        # Update data di session state
        st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)

        st.success("✅ Data berhasil disimpan!")
        st.dataframe(st.session_state["data"])  # Tampilkan data terbaru
    except Exception as e:
        st.error(f"❌ Gagal menyimpan data: {e}")

# Tombol Prediksi
if st.button("Prediksi"):
    if len(st.session_state["data"]) >= 90:  # Cek apakah data cukup
        st.session_state["updated_data"] = st.session_state["data"]
        st.write("🔗 Data sudah siap untuk prediksi. Buka halaman hasil prediksi.")
    else:
        st.warning("⚠️ Data tidak cukup untuk prediksi. Dibutuhkan minimal 90 data.")
