import os
import time
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page  # Import title page function

def fetch_facebook_chats(driver, pdf_report, fb_username, pin):
    """Fetches Facebook chats and adds them to the PDF report."""
    # Create folder for saving chat screenshots inside 'Data'
    data_folder = os.path.join("./Facebook/Data", f"Data_{fb_username}", "Chats")
    os.makedirs(data_folder, exist_ok=True)

    # Add title page for chats section
    create_title_page(pdf_report, "CHATS")

    # Navigate to Facebook messages
    messages_url = "https://www.facebook.com/messages/t/"
    driver.get(messages_url)
    time.sleep(5)

    # Check if the PIN input appears and handle it
    try:
        pin_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#mw-numeric-code-input-prevent-composer-focus-steal"))
        )
        pin_input.clear()
        pin_input.send_keys(pin)
        
        # Wait for the PIN submission process
        time.sleep(2)
    except Exception as e:
        print("No PIN input found, proceeding without entering PIN.")

    # Scroll to load more messages
    previous_height = driver.execute_script("return document.body.scrollHeight")
    chat_links = []

    while True:
        time.sleep(2)

        # Find all chat divs and extract their href
        chat_divs = driver.find_elements(By.XPATH, '//div[contains(@class, "x1n2onr6")]//div[contains(@class, "x78zum5 xdt5ytf") and @data-virtualized="false"]')
        for chat_div in chat_divs:
            anchors = chat_div.find_elements(By.TAG_NAME, 'a')
            for anchor in anchors:
                href = anchor.get_attribute('href')
                if href and href not in chat_links:
                    chat_links.append(href)

        # Scroll down to load more chats
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == previous_height:
            break
        previous_height = new_height

    # Define PDF dimensions
    width, height = A4
    margin = 30
    image_spacing = 20

    # Iterate through each chat and take screenshots
    for index, chat_link in enumerate(chat_links):
        try:
            driver.get(chat_link)
            time.sleep(5)

            screenshot_path = os.path.join(data_folder, f"chat_{index + 1}.png")
            driver.save_screenshot(screenshot_path)

            img = Image.open(screenshot_path)
            img_width, img_height = img.size
            aspect_ratio = img_height / img_width

            img_pdf_width = width - 2 * margin
            img_pdf_height = img_pdf_width * aspect_ratio

            if img_pdf_height > (height - 2 * margin):
                img_pdf_height = height - 2 * margin
                img_pdf_width = img_pdf_height / aspect_ratio

            x = (width - img_pdf_width) / 2
            y = height - margin - img_pdf_height

            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()

        except Exception as e:
            print(f"Error processing chat {index + 1}: {e}")
            continue
