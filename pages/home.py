import streamlit as st

st.title("Aplikasi Prediksi Harga Beras")
st.write("Selamat datang di aplikasi prediksi harga beras.")

# Buat sidebar untuk navigasi
menu = st.sidebar.radio("Pilih Menu", ["Home", "Preprocessing", "Input", "Output"])

if menu == "Preprocessing":
    try:
        # Membaca file dengan encoding utf-8
        with open("preprocessing.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except UnicodeDecodeError:
        st.error("Terjadi kesalahan encoding pada file preprocessing.py. Coba periksa encoding file.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat file preprocessing.py: {e}")

# Halaman Input
elif menu == "Input":
    try:
        # Membaca file dengan encoding utf-8
        with open("input.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except UnicodeDecodeError:
        st.error("Terjadi kesalahan encoding pada file preprocessing.py. Coba periksa encoding file.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat file preprocessing.py: {e}")

# Halaman Output
elif menu == "Output":
    try:
        # Membaca file dengan encoding utf-8
        with open("output.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except UnicodeDecodeError:
        st.error("Terjadi kesalahan encoding pada file output.py. Coba periksa encoding file.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat file output.py: {e}")


# Home
else:
    st.write("Gunakan sidebar untuk navigasi ke menu lainnya.")
