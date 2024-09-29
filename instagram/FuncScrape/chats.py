from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page
from FuncScrape.pdf_utils import scale_image

def fetch_chats(driver, pdf_report, u_name):
    """Fetches Instagram chats of a user and adds them to the PDF report."""
    driver.get('https://www.instagram.com/direct/inbox/')
    time.sleep(5)

    # Handle any initial pop-up alerts
    try:
        alert = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]')))
        alert.click()
    except Exception as e:
        print("No initial alert found or an error occurred:", e)

    # Step 1: Open chat list and process each chat
    chat_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x13dflua.x19991ni')))
    print(f"Found {len(chat_divs)} chats.")

    path = os.path.join("./instagram/Data", f"Data_{u_name}","Chats")
    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "CHATS")
    # Add title page for chats
    width, height = A4
    

    # Step 2: Process each chat, take screenshots, and add to PDF
    for index, chat_div in enumerate(chat_divs):
        try:
            # Open the chat
            chat_button = chat_div.find_element(By.CSS_SELECTOR, 'div[role="button"]')
            chat_button.click()
            time.sleep(5)

            # Take a screenshot of the chat
            screenshot_path = os.path.join(path, f"chat_{index + 1}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved for chat {index + 1}.")

            # Add screenshot to the PDF
            img = Image.open(screenshot_path)
            img_pdf_width, img_pdf_height = scale_image(img, width - 2 * 30, height - 2 * 30)
            x = (width - img_pdf_width) / 2
            y = (height - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()

        except Exception as e:
            print(f"Error processing chat {index + 1}: {e}")
