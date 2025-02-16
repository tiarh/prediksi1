import pandas as pd

def load_data():
    try:
        # Memuat semua data secara langsung
        beras = pd.read_csv("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/data_Bangkalan_beras_quality_medium_1.csv", encoding='utf-8', on_bad_lines='skip')
        suhu = pd.read_csv("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Temperature_2019_2024%20new.csv", encoding='utf-8', on_bad_lines='skip')
        hujan = pd.read_csv("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Rainfall_2019_2024.csv", encoding='utf-8', on_bad_lines='skip')
        udara = pd.read_csv("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Pressure_2019_2024%203%20f.csv", encoding='utf-8', on_bad_lines='skip')
        kelembapan = pd.read_csv("https://raw.githubusercontent.com/tiarh/prediksi-beras/refs/heads/main/Bangkalan_Dew_Point_Daily_2019_2024c.csv", encoding='utf-8', on_bad_lines='skip')

        print("Berhasil memuat semua data.")
        
        return {
            "beras": beras,
            "suhu": suhu,
            "hujan": hujan,
            "udara": udara,
            "kelembapan": kelembapan
        }

    except Exception as e:
        print(f"Error memuat data: {e}")
        return None
