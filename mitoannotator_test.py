from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# 1. Read the text from your local file
# Replace 'sequences.txt' with the actual path to your file
file_path = "test_reads/PX734717.1.fa"
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
    "plugins.always_open_pdf_externally": True,  # <-- The Magic Key: Forces immediate download instead of embedding
}
options.add_experimental_option("prefs", prefs)


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

    # 4. Find the button and click it
    # (Ensure you update this selector to match your actual button)
    # submit_button = wait.until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-success"))
    # )
    # driver.execute_script("arguments[0].click();", submit_button)
    # print("Annotate button clicked via JavaScript")

    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-success"))
    )

    submit_button.click()
    print("Annotate button clicked successfully?")

    # # Give the toast up to 4 seconds to pop up on the screen
    # time.sleep(10)

    # # Search specifically for the error toast component
    # error_toasts = driver.find_elements(By.CSS_SELECTOR, "#error-toast")

    # if error_toasts:
    #     error_toast = error_toasts[0]
    #     # Check if the toast has the active 'show' class or is visible
    #     if "show" in error_toast.get_attribute("class") or error_toast.is_displayed():
    #         print(f"Toast Warning Found: {error_toast.text}")
    #         print("Retrying: Clicking the Annotate button a second time...")

    #         # Re-locate and force click the submit button again
    #         submit_button = wait.until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-success"))
    #         )
    #         time.sleep(2)
    #         driver.execute_script("arguments[0].click();", submit_button)
    #         print("Annotate button clicked a second time.")

    #         # Wait another moment to see if it clears the pipeline
    #         time.sleep(3)

    processing_wait = WebDriverWait(driver, 60)

    view_results_button = processing_wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[href^='/annotation/result']")
        )
    )

    # 5. Force the browser to click via JavaScript (ignores coordinate obstructions)
    driver.execute_script("arguments[0].click();", view_results_button)
    print("View Results button clicked via JavaScript successfully!")

    # 6. Crucial Step: Switch Selenium's focus to the newly opened tab
    # 'window_handles[-1]' always represents the most recently opened tab
    wait.until(lambda d: len(d.window_handles) > 1)  # Wait for tab to open
    driver.switch_to.window(driver.window_handles[-1])

    print("Switched focus to new window")

    # 7. Wait for the download link to appear on the new results page
    # Targets the <a> tag containing the word "Download"
    download_link = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[href*='mitoannotator.tar.gz']")
        )
    )

    driver.execute_script("arguments[0].click();", download_link)
    print(".tar.gz Download triggered successfully with JavaScript!")


    view_pdf_button = processing_wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[href^='/annotation/result']")
        )
    )

    # 5. Force the browser to click via JavaScript (ignores coordinate obstructions)
    driver.execute_script("arguments[0].click();", view_results_button)
    print("View Results button clicked via JavaScript successfully!")

    #     # 7. Wait for the PDF embed element to render on the page
    # # Targets the <embed> tag inside the 'ratio' container class
    # pdf_element = wait.until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "div.ratio embed"))
    # )

    # # Selenium automatically resolves the relative path into a full absolute URL
    # pdf_absolute_url = pdf_element.get_attribute("src")
    # print(f"Dynamically extracted PDF URL: {pdf_absolute_url}")

    # # Navigate directly to the absolute PDF link
    # # Because of our Chrome configurations, this immediately triggers a background download
    # driver.get(pdf_absolute_url)
    # print("PDF download successfully initiated!")

    # Allow a few seconds for the file pipeline to finish writing to disk
    time.sleep(5)

    # 8. Crucial: Pause to allow the file to finish transferring to your machine
    # Adjust this if your tar.gz files are very large
    # time.sleep(10)

    # Optional pause to see the result
    time.sleep(120)

finally:
    # Close the browser
    driver.quit()
