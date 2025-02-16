import pandas as pd

def load_data():
    # Lokasi file
    file_paths = {
        "beras": "https://drive.google.com/file/d/1ej1uFHp6Zo9r0isP_Yim6lARZQ9jhKI_/view?usp=drive_link",
        "suhu": "https://drive.google.com/file/d/1oAeMwvSgNmuD0uNZ8R8naX0HJ6cZsOLa/view?usp=drive_link",
        "hujan": "https://drive.google.com/file/d/1wIieKsJORhARaTjkcWnOEy-2WNjTrRM6/view?usp=drive_link",
        "udara": "https://drive.google.com/file/d/1WBFKP6teIowOwpZeEKIjG_zoFT3rog_i/view?usp=drive_link",
        "kelembapan": "https://drive.google.com/file/d/1X4EZgnHWVNf0h_sFlehh3Gv4NRe0xwNE/view?usp=drive_link",
    }
    
    # Memuat semua data
    data_frames = {}
    for name, path in file_paths.items():
        try:
            data_frames[name] = pd.read_csv(path)
            print(f"Berhasil memuat data {name}")
        except Exception as e:
            print(f"Error memuat data {name}: {e}")
            data_frames[name] = None
    
    return data_frames
