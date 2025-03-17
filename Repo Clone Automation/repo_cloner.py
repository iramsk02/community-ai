import os
import time
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set your download directory (absolute path)
download_dir = os.path.abspath("downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize the Chrome driver (ensure chromedriver is in your PATH)
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the GitHub repository page
    repo_url = "https://github.com/openMF/mifos-gazelle?tab=readme-ov-file"  # add ur repos, if needed i will write a function take multiple repo input to extract effectively
    driver.get(repo_url)
    
    # Wait until the "Code" button is clickable and click it.But here (//span[contains(text(), 'Code')]) isnt a unique locator so i have to use below provided one, this has tendency to change if github updates their frontend
    wait = WebDriverWait(driver, 10)
    code_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-variant='primary']//span[contains(@class, 'prc-Button-Label-pTQ')]")))
    code_button.click()
    
    # this is the download zip locator which is unique
    download_zip = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Download ZIP')]")))
    download_zip.click()
    
    # Wait for the ZIP file to appear in the download folder (timeout after 60 seconds)
    zip_filename = None
    timeout = 60  # seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        for filename in os.listdir(download_dir):
            if filename.endswith(".zip"):
                zip_filename = filename
                break
        if zip_filename:
            break
        time.sleep(1)
    
    if not zip_filename:
        print("Download timed out or ZIP file not found.")
    else:
        zip_path = os.path.join(download_dir, zip_filename)
        print(f"Downloaded file: {zip_path}")
        
        # Unzip the downloaded archive into a subfolder called "extracted"
        extract_dir = os.path.join(download_dir, "extracted")
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"Extracted ZIP contents to: {extract_dir}")

finally:
    driver.quit()
