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
# Replace 'sequences.txt' with the actual path to your file
file_path = "test_reads/NC_023807.1.fa"
base_name = os.path.splitext(os.path.basename(file_path))[0]
print(base_name)

if not os.path.exists(file_path):
    raise FileNotFoundError(
        f"Could not find the file at {file_path}. Please check the path."
    )

with open(file_path, "r", encoding="utf-8") as file:
    fasta_data = file.read()

download_dir = os.path.expanduser(f"~/Downloads/{base_name}")

os.makedirs(download_dir, exist_ok=True)


# Create Chrome Options
options = Options()
prefs = {
    "download.default_directory": download_dir,  # Set your preferred download folder path
    "download.prompt_for_download": False,  # Disable popup prompts
    "download.directory_upgrade": True,
    # "plugins.always_open_pdf_externally": True,  # <-- The Magic Key: Forces immediate download instead of embedding
}
options.add_experimental_option("prefs", prefs)
# options.add_argument("--start-maximized")
# options.add_argument("--auto-open-devtools-for-tabs")

# 1. Initialize the Chrome browser
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

try:
    # 2. Open the target webpage
    url = "https://mitofish.aori.u-tokyo.ac.jp/annotation/input"  # Replace with your target URL
    driver.get(url)

    time.sleep(5)

    # Wait for the text box to be present (adjust locator: ID, NAME, XPATH, etc.)
    wait = WebDriverWait(driver, 10)
    text_box = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-v-4267c46e]"))
    )

    # time.sleep(5)
    # 3. Paste or send text into the box
    text_to_paste = fasta_data
    text_box.clear()  # Clears existing text if needed
    text_box.send_keys(text_to_paste)
    print("data pasted into text box")
    # time.sleep(10)

    # 4. Find the Annotate! button and click it
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success"))
    )

    submit_button.click()
    print("Annotate button clicked successfully?")

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

    # 7. Wait for the download link to appear on the new results page
    download_wait = WebDriverWait(driver, 60)
    download_link = download_wait.until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(@href, ".mitoannotator.tar.gz")]'))
    )
    
    # 3. Extract the direct download URL from the 'href' attribute
    targz_url = download_link.get_attribute("href")
    print(f"Found archive URL: {targz_url}")
    
    targz_filename = (f"{base_name}.tar.gz")
    urllib.request.urlretrieve(targz_url, Path(download_dir, targz_filename))
    print(f"Successfully downloaded to {Path(download_dir, targz_filename)}")



    # driver.execute_script("arguments[0].click();", download_link)
    # print(".tar.gz Download triggered successfully with JavaScript!")

    # 8. wait for pdf to load in; click download button
    # Adjust the timeout (10 seconds) if the page loads slowly
    pdf_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//embed[contains(@src, "seq.pdf")]'))
    )
    print("embedded pdf element located")

    # 3. Extract the PDF URL from the 'src' attribute
    pdf_url = pdf_element.get_attribute("src")
    print(f"Found PDF URL: {pdf_url}")

    # 4. Download the PDF file using urllib
    pdf_filename = (f"{base_name}_plot.pdf")
    urllib.request.urlretrieve(pdf_url, Path(download_dir, pdf_filename))
    print(f"Successfully downloaded to {Path(download_dir, pdf_filename)}")

    print("successfully annotated mitogenome and downloaded files")

finally:
    # Close the browser
    driver.quit()
