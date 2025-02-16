import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta

bulan_mapping = {
    "Januari": "January",
    "Februari": "February",
    "Maret": "March",
    "April": "April",
    "Mei": "May",
    "Juni": "June",
    "Juli": "July",
    "Agustus": "August",
    "September": "September",
    "Oktober": "October",
    "November": "November",
    "Desember": "December"
    }

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Mode headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile-unique")
    
    # Sesuaikan dengan lokasi Chrome yang telah diunduh
    chrome_options.binary_location = "/usr/local/bin/google-chrome"
    # Sesuaikan dengan lokasi chromedriver yang telah diunduh
    service = Service("/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
def initialize_elements(driver):
    try:
        dropdown_komoditas = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="ddbCategory"]//input[@type="text"]'))
        )
        dropdown_komoditas.click()
        time.sleep(1)

        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//li[@role='treeitem' and contains(@aria-label, 'Beras') and @aria-level='1']"))
        )

        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(1)

        medium_beras_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//li[@role='treeitem' and contains(@aria-label, 'Beras Kualitas Medium I') and @aria-level='2']"))
        )

        medium_beras_element.click()
        time.sleep(1)

        jenis_pasar_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[1]'))
        )
        jenis_pasar_dropdown.click()
        time.sleep(1)

        pasar_modern_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "dx-item-content") and contains(text(), "Pasar Modern")]'))

        )
        pasar_modern_option.click()
        time.sleep(1)

        provinsi_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[2]'))
        )
        provinsi_dropdown.click()
        time.sleep(1)

        driver.execute_script("""
            var items = document.querySelectorAll('div.dx-scrollable-content .dx-item-content.dx-list-item-content');
            for (var i = 0; i < items.length; i++) {
                if (items[i].textContent.includes('Jawa Timur')) {
                    items[i].click();
                    break;
                }
            }
        """)
        time.sleep(1)

        kabupaten_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[3]'))
        )
        kabupaten_dropdown.click()
        time.sleep(2)

        driver.execute_script("""
            var items = document.querySelectorAll('div.dx-scrollable-content .dx-item-content.dx-list-item-content');
            for (var i = 0; i < items.length; i++) {
                if (items[i].textContent.includes('Bangkalan')) {
                    items[i].click();
                    break;
                }
            }
        """)
        time.sleep(1)
        
    except Exception as e:
        print(f"Error initializing elements: {e}")

def navigate_to_month(driver, target_date):
    target_date = datetime.strptime(target_date, '%Y-%m-%d')
    target_month = target_date.month
    target_year = target_date.year

    while True:
        try:
            current_month_year_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'dx-calendar-caption-button') and contains(@class, 'dx-button-has-text')]//span[@class='dx-button-text']"))
            )
            current_month_year = current_month_year_element.text.strip()

            if not current_month_year:
                print("Element text is empty, retrying...")
                continue

            try:
                parts = current_month_year.split()
                if len(parts) != 2:
                    raise ValueError("Invalid month/year format.")
                
                current_month_str, current_year = parts
                current_year = int(current_year)
                current_month_str = current_month_str.capitalize()

                current_month_eng = bulan_mapping.get(current_month_str, current_month_str)
                current_month = datetime.strptime(current_month_eng, '%B').month
            except ValueError as ve:
                print(f"Error parsing month/year: {ve}")
                break

            if current_month == target_month and current_year == target_year:
                break

            if (current_year < target_year) or (current_year == target_year and current_month < target_month):
                chevron_next = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and @aria-label='chevronright']"))
                )
                chevron_next.click()
                print("Navigating to next month.")
            else:
                chevron_prev = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and @aria-label='chevronleft']"))
                )
                chevron_prev.click()
                print("Navigating to previous month.")
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in navigate_to_month: {e}")
            break


def fetch_price(driver, date):
    try:
        tanggal_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='dboDate']//div[@role='button']"))
        )
        tanggal_button.click()
        time.sleep(1)

        navigate_to_month(driver, date)

        tanggal_yang_diinginkan = datetime.strptime(date, '%Y-%m-%d')
        tanggal_data_value = tanggal_yang_diinginkan.strftime('%Y/%m/%d')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//td[@data-value='{tanggal_data_value}']"))
        ).click()

        tombol_tampilkan = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="devextreme11"]'))
        )
        tombol_tampilkan.click()
        time.sleep(1)

        harga_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//td[@aria-describedby="dx-col-2"][@style="text-align: right;"]'))
        )
        return harga_element.text.strip()

    except Exception as e:
        print(f"Error in fetch_price: {e}")
        return None

def crawl_data_for_bangkalan(start_date, end_date):
    driver = get_driver()
    driver.get('https://www.bi.go.id/hargapangan#')
    initialize_elements(driver)

    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    file_name = "data_Bangkalan_beras_quality_medium_1_baru_test.csv"
    with open(file_name, 'w') as file:
        file.write("Date,Kabupaten,Price\n")
        
        while current_date <= end_date_obj:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"Fetching data for date: {date_str}")

            price = fetch_price(driver, date_str)
            if price:
                print(f"Price on {date_str}: {price}")
                file.write(f"{date_str},Bangkalan,{price}\n")
            else:
                print(f"No price data found for {date_str}")

            current_date += timedelta(days=1)

    driver.quit()

crawl_data_for_bangkalan('2019-08-01', '2025-02-01')
