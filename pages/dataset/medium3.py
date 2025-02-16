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

bulan_mapping = {
    "Januari": "January", "Februari": "February", "Maret": "March",
    "April": "April", "Mei": "May", "Juni": "June",
    "Juli": "July", "Agustus": "August", "September": "September",
    "Oktober": "October", "November": "November", "Desember": "December"
}

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile-unique")
    chrome_options.binary_location = "/usr/local/bin/google-chrome"
    service = Service("/usr/local/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def navigate_to_month(driver, target_date):
    target_date = datetime.strptime(target_date, '%Y-%m-%d')
    target_month = target_date.month
    target_year = target_date.year

    while True:
        try:
            current_month_year_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'dx-calendar-caption-button')]//span[@class='dx-button-text']"))
            )
            current_month_year = current_month_year_element.text.strip()

            parts = current_month_year.split()
            if len(parts) != 2:
                raise ValueError("Invalid month/year format.")
            
            current_month_str, current_year = parts
            current_year = int(current_year)
            current_month_str = current_month_str.capitalize()
            current_month_eng = bulan_mapping.get(current_month_str, current_month_str)
            current_month = datetime.strptime(current_month_eng, '%B').month

            if current_month == target_month and current_year == target_year:
                break

            if (current_year < target_year) or (current_year == target_year and current_month < target_month):
                chevron_next = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and @aria-label='chevronright']"))
                )
                chevron_next.click()
            else:
                chevron_prev = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and @aria-label='chevronleft']"))
                )
                chevron_prev.click()
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in navigate_to_month: {e}")
            break

def fetch_price(driver, date):
    try:
        driver.get('https://www.bi.go.id/hargapangan#')
        time.sleep(3)
        
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="ddbCategory"]//input[@type="text"]'))
        )
        dropdown.click()
        time.sleep(2)
        
        beras_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@aria-label, 'Beras Kualitas Medium I')]"))
        )
        beras_option.click()
        
        pasar_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list"])[1]'))
        )
        pasar_dropdown.click()
        time.sleep(2)
        
        pasar_modern = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Pasar Modern")]'))
        )
        pasar_modern.click()
        
        kabupaten_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list"])[3]'))
        )
        kabupaten_dropdown.click()
        time.sleep(2)
        
        bangkalan_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Bangkalan")]'))
        )
        bangkalan_option.click()
        
        tanggal_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='dboDate']//div[@role='button']"))
        )
        tanggal_button.click()
        time.sleep(1)
        
        navigate_to_month(driver, date)
        
        tanggal_yang_diinginkan = datetime.strptime(date, '%Y-%m-%d').strftime('%Y/%m/%d')
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//td[@data-value='{tanggal_yang_diinginkan}']"))
        ).click()
        
        tampilkan = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="devextreme11"]'))
        )
        tampilkan.click()
        time.sleep(1)
        
        harga_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//td[@aria-describedby="dx-col-2"][@style="text-align: right;"]'))
        )
        return harga_element.text.strip()
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def main():
    today = datetime.today().strftime('%Y-%m-%d')
    start_date = "2025-02-02"

    if today < start_date:
        print("Crawling belum dimulai")
        return
    
    driver = get_driver()
    harga = fetch_price(driver, today)
    driver.quit()
    
    if harga:
        print(f"Harga Beras Kualitas Medium I di Bangkalan: {harga}")
    else:
        print("Data tidak tersedia")

if __name__ == "__main__":
    main()
