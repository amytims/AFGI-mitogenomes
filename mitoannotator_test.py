from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time
import os
import urllib.request

# 1. Read the text from your local file

# to do programattically - external option?
file_path = "test_reads/NC_023807.1.fa"
base_name = os.path.splitext(os.path.basename(file_path))[0]
print(base_name)

if not os.path.exists(file_path):
    raise FileNotFoundError(
        f"Could not find the file at {file_path}. Please check the path."
    )

with open(file_path, "r", encoding="utf-8") as file:
    fasta_data = file.read()


# specify externally
download_dir = os.path.expanduser(f"~/Downloads/{base_name}")

# make directory if needed
os.makedirs(download_dir, exist_ok=True)

# Create Chrome Options
options = Options()
prefs = {
    "download.default_directory": download_dir,  # Set your preferred download folder path
    "download.prompt_for_download": False,  # Disable popup prompts
    "download.directory_upgrade": True,
}
options.add_experimental_option("prefs", prefs)

# 1. Initialize the Chrome browser
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

try:
    # 2. Open the target webpage
    url = "https://mitofish.aori.u-tokyo.ac.jp/annotation/input" 
    driver.get(url)

    #wait a sec so mitofish doesn't freak out
    time.sleep(3)

    # Wait for the text box to be present in case it takes longer to load
    wait = WebDriverWait(driver, 10)
    text_box = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-v-4267c46e]"))
    )


    # 3. Paste or send text into the box
    text_to_paste = fasta_data
    text_box.clear()  # Clears existing text if needed
    text_box.send_keys(text_to_paste)
    print("data pasted into text box")


    # 4. Find the Annotate! button and click it
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success"))
    )

    submit_button.click()
    print("Annotate button clicked successfully")

    # TRYING TO CLICK WITH JAVASCRIPT CAUSES AN ERROR
    # HAVE TO DO IT WITH CLICK()
    # submit_button = wait.until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-success"))
    # )
    # driver.execute_script("arguments[0].click();", submit_button)
    # print("Annotate button clicked via JavaScript")

    # 5. Wait for results to load and click "view results" button
    processing_wait = WebDriverWait(driver, 60)
    view_results_button = processing_wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[href^='/annotation/result']")
        )
    )

    driver.execute_script("arguments[0].click();", view_results_button)
    print("View Results button clicked via JavaScript successfully!")

    # 6. Switch Selenium's focus to the newly opened tab
    # 'window_handles[-1]' always represents the most recently opened tab
    wait.until(lambda d: len(d.window_handles) > 1)  # Wait for tab to open
    driver.switch_to.window(driver.window_handles[-1])

    print("Switched focus to new window")

    # 7. Wait for the tar.gz download link to appear on the new results page
    download_wait = WebDriverWait(driver, 60)
    download_link = download_wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//a[contains(@href, ".mitoannotator.tar.gz")]')
        )
    )

    # Extract the direct download URL from the 'href' attribute
    targz_url = download_link.get_attribute("href")
    print(f"Found archive URL: {targz_url}")

    # download and rename tar.gz file to match input file name
    targz_filename = f"{base_name}.tar.gz"
    urllib.request.urlretrieve(targz_url, Path(download_dir, targz_filename))
    print(f"Successfully downloaded to {Path(download_dir, targz_filename)}")


    # 8. wait for pdf to load in; click download button
    pdf_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//embed[contains(@src, "seq.pdf")]'))
    )
    print("embedded pdf element located")

    # Extract the PDF URL from the 'src' attribute
    pdf_url = pdf_element.get_attribute("src")
    print(f"Found PDF URL: {pdf_url}")

    # Download the PDF file using urllib
    pdf_filename = f"{base_name}_plot.pdf"
    urllib.request.urlretrieve(pdf_url, Path(download_dir, pdf_filename))
    print(f"Successfully downloaded to {Path(download_dir, pdf_filename)}")

    print("successfully annotated mitogenome and downloaded files")

finally:
    # Close the browser
    driver.quit()
