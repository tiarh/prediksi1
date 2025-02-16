import os
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile-unique")
    chrome_options.binary_location = "/usr/local/bin/google-chrome"
    service = Service("/usr/local/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def fetch_price(driver, date):
    try:
        driver.get('https://www.bi.go.id/hargapangan#')
        time.sleep(3)  # Tunggu page load (sesuaikan dengan koneksi)
        
        # Pilih Beras Kualitas Medium I di dropdown
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="ddbCategory"]//input[@type="text"]'))
        )
        dropdown.click()
        time.sleep(5)
        beras_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@aria-label, 'Beras Kualitas Medium I')]")
        ))
        beras_option.click()
        
        # Pilih Pasar Modern
        pasar_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list"])[1]'))
        )
        pasar_dropdown.click()
        time.sleep(5)
        pasar_modern = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Pasar Modern")]'))
        )
        pasar_modern.click()
        
        # Pilih Kabupaten Bangkalan
        kabupaten_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list"])[3]'))
        )
        kabupaten_dropdown.click()
        time.sleep(5)
        bangkalan_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Bangkalan")]'))
        )
        bangkalan_option.click()
        
        # Pilih tanggal
        tanggal_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='dboDate']//div[@role='button']"))
        )
        tanggal_button.click()
        time.sleep(1)
        tanggal_yang_diinginkan = date.strftime('%Y/%m/%d')
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//td[@data-value='{tanggal_yang_diinginkan}']"))
        ).click()
        
        # Klik tombol tampilkan
        tampilkan = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="devextreme11"]'))
        )
        tampilkan.click()
        time.sleep(1)
        
        # Ambil harga
        harga_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//td[@aria-describedby="dx-col-2"][@style="text-align: right;"]'))
        )
        return harga_element.text.strip()
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def save_to_temp(date, kabupaten, price):
    temp_file = "temp_data.csv"
    data = [date, kabupaten, price]
    
    file_exists = os.path.exists(temp_file)
    with open(temp_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Kabupaten", "Price"])  # Header jika file baru
        writer.writerow(data)

def move_temp_to_combined():
    temp_file = "temp_data.csv"
    combined_file = "combined_data.csv"
    
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as file:
            rows = list(csv.reader(file))
            header, data = rows[0], rows[1:]
        
        # Cek jika ada 5 data pada tanggal yang sama
        if len(data) >= 5:
            with open(combined_file, 'a', newline='') as file:
                writer = csv.writer(file)
                if not os.path.exists(combined_file):
                    writer.writerow(header)  # Header jika file baru
                writer.writerows(data)  # Pindahkan data
            os.remove(temp_file)  # Hapus temp setelah dipindah

def main():
    today = datetime.today()
    start_date = datetime(2025, 2, 2)
    if today < start_date:
        print("Crawling belum dimulai")
        return
    
    driver = get_driver()
    harga = fetch_price(driver, today)
    driver.quit()
    
    if harga:
        save_to_temp(today.strftime('%Y-%m-%d'), "Bangkalan", harga)
        move_temp_to_combined()
    else:
        print("Data tidak tersedia")

if __name__ == "__main__":
    main()
