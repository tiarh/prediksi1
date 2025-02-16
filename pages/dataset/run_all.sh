
#!/bin/bash

# Aktifkan Virtual Environment
source /root/prediksi/venv/bin/activate

# Jalankan script Python
python3 /root/prediksi/pages/dataset/medium4.py
python3 /root/prediksi/pages/dataset/curah_hujan4.py
python3 /root/prediksi/pages/dataset/suhu4.py
python3 /root/prediksi/pages/dataset/kelembapan4.py
python3 /root/prediksi/pages/dataset/tekanan_udara4.py
python3 /root/prediksi/pages/dataset/to_combined.py
# Nonaktifkan Virtual Environment
deactivate
