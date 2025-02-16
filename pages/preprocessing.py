import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    try:
        max_rows = 100000

        def read_csv_optimized(url, nrows=max_rows):
            return pd.read_csv(url, encoding="utf-8", on_bad_lines="skip", nrows=nrows)

        beras = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/data_Bangkalan_beras_quality_medium_1.csv")
        suhu = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/mean_temperature_bangkalan.csv")
        hujan = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/daily_mean_precipitation_bangkalan.csv")
        udara = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/mean_surface_pressure_bangkalan.csv")
        kelembapan = read_csv_optimized("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/mean_dewpoint_bangkalan.csv")

        return {"beras": beras, "suhu": suhu, "hujan": hujan, "udara": udara, "kelembapan": kelembapan}

    except Exception as e:
        st.error(f"❌ Error memuat atau memproses data: {e}")
        return None

@st.cache_data
def load_preprocessed_data(scenario_url):
    try:
        return pd.read_csv(scenario_url)
    except Exception as e:
        st.error(f"❌ Gagal memuat data skenario: {e}")
        return None

st.title("📂 Data Mentah dan Hasil Preprocessing")
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

lag_options = [30, 60, 90]
scenario_urls = {
    30: "https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/normalized_data_skenario1%20(1).csv",
    60: "https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/normalized_data_skenario2%20(1).csv",
    90: "https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/baru/normalized_data_skenario3%20(1).csv"
}

selected_lag = st.selectbox("⏳ Pilih Lag (steps in):", lag_options)
if st.button("🚀 Tampilkan Hasil Preprocessing"):
    scenario_url = scenario_urls.get(selected_lag)
    preprocessed_data = load_preprocessed_data(scenario_url)
    if preprocessed_data is not None:
        st.subheader(f"📂 Data Preprocessed untuk Lag {selected_lag} (Skenario {lag_options.index(selected_lag)+1})")
        st.dataframe(preprocessed_data.head())
