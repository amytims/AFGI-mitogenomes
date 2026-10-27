#!/usr/bin/env python3

# 1. parse fasta file - check its extension and open file
# 2. parse and create download directory
# 3. open browser, paste in fasta file, click annotate button
# 4. view results in new tab
# 5. download .tar.gz and .pdf files

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time
import os
import urllib.request
import argparse
import gzip

parser = argparse.ArgumentParser(description="Run a target fasta (compressed or uncompressed) through the MitoAnnotator process on MitoFish")

# Parse external options
parser.add_argument(
    "-f", "--fasta", help="path to input fasta file", required=True, type=str
)
parser.add_argument(
    "-d",
    "--download_dir",
    help="path to download parent directory. Files will be saved in download_dir/fasta/",
    type=str,
    default="~/Downloads",
)

args = parser.parse_args()

# parse fasta file path
file_path = Path(args.fasta)

# error if file doesn't exist
if not os.path.exists(file_path):
    raise FileNotFoundError(
        f"Could not find the file at {file_path}. Please check the path."
    )


# if it's a compressed file, open with gzip open
if file_path.suffix.lower() in [".gz"]:
    # make sure it's either.fa.gz or .fasta.gz - throw error if not
    if not file_path.with_suffix("").suffix.lower() in [".fa", ".fasta"]:
        raise TypeError(
            "File does not have .fa or .fasta extension - check it's a valid fasta file"
        )

    with gzip.open(file_path, "rt", encoding="utf-8") as file:
        fasta_data = file.read()
        
# if it's not compressed, make sure it's a .fa or .fasta file and then open
else:
    if not file_path.suffix.lower() in [".fa", ".fasta"]:
        raise TypeError(
            "File does not have .fa or .fasta extension - check it's a valid fasta file"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        fasta_data = file.read()


print(f"Processing fasta file at {file_path}")

# get file name without extensions
base_name = (
    os.path.basename(file_path)
    .removesuffix(".gz")
    .removesuffix(".fasta")
    .removesuffix(".fa")
)
download_dir = os.path.expanduser(f"{args.download_dir}/{base_name}")

# make directory; throw error if it already exists - make sure to not overwrite existing files
os.makedirs(download_dir, exist_ok=False)

print(f"Files will be saved in {download_dir}/")


# Initialize the Chrome browser
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

try:
    # Open the mitoannotator webpage
    url = "https://mitofish.aori.u-tokyo.ac.jp/annotation/input"
    driver.get(url)

    # wait a sec so it doesn't freak out
    time.sleep(3)

    # Wait for the text box to be present in case it takes longer to load
    textbox_wait = WebDriverWait(driver, 10)
    text_box = textbox_wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-v-4267c46e]"))
    )

    # paste fasta data into the text box
    text_to_paste = fasta_data
    text_box.clear()  # Clears existing text if needed
    text_box.send_keys(text_to_paste)
    print("Fasta data pasted into text box")


    # Find the Annotate! button and click it
    # TRYING TO CLICK WITH JAVASCRIPT CAUSES AN ERROR
    # HAVE TO DO IT WITH CLICK()
    submit_button_wait = WebDriverWait(driver, 30)
    submit_button = submit_button_wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success"))
    )

    submit_button.click()
    print("'Annotate!' button clicked successfully")


    # Wait for results to load and click "view results" button
    processing_wait = WebDriverWait(driver, 60)
    view_results_button = processing_wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[href^='/annotation/result']")
        )
    )

    driver.execute_script("arguments[0].click();", view_results_button)
    print("'View Results' button successfully clicked using JavaScript")

    # Switch Selenium's focus to the newly opened tab
    window_wait = WebDriverWait(driver, 30)
    window_wait.until(lambda d: len(d.window_handles) > 1)  # Wait for tab to open
    driver.switch_to.window(driver.window_handles[-1])

    print("Switched browser focus to results tab")

    # Wait for the tar.gz download link to appear on the new results page
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
    print(f"Successfully downloaded .tar.gz to {Path(download_dir, targz_filename)}")

    # Wait for pdf to load in; click download button
    pdf_wait = WebDriverWait(driver, 30)
    pdf_element = pdf_wait.until(
        EC.presence_of_element_located((By.XPATH, '//embed[contains(@src, "seq.pdf")]'))
    )

    # Extract the PDF URL from the 'src' attribute
    pdf_url = pdf_element.get_attribute("src")
    print(f"Found PDF URL: {pdf_url}")

    # Download the PDF file using urllib
    pdf_filename = f"{base_name}_plot.pdf"
    urllib.request.urlretrieve(pdf_url, Path(download_dir, pdf_filename))
    print(f"Successfully downloaded .pdf to {Path(download_dir, pdf_filename)}")

    print("Successfully annotated mitogenome and downloaded files. \nExiting browser window.")
    time.sleep(3)

finally:
    # Close the browser
    driver.quit()
