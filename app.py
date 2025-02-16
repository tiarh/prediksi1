import streamlit as st
from pathlib import Path

# Halaman Utama
st.sidebar.title("Navigasi")
menu = st.sidebar.radio(
    "Pilih Menu",
    ("Home", "Preprocessing", "Input", "Output")
)

# Panggil file sesuai pilihan menu
if menu == "Home":
    exec(Path("pages/home.py").read_text())
elif menu == "Preprocessing":
    exec(Path("pages/preprocessing.py").read_text())
elif menu == "Input":
    exec(Path("pages/input.py").read_text())
elif menu == "Output":
    exec(Path("pages/output.py").read_text())
