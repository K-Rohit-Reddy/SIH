from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Setup WebDriver
service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get("http://www.instagram.com")

time.sleep(6)

# Log in to Instagram
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
u_name = ""
passw = ""
username.clear()
password.clear()
username.send_keys(u_name)
password.send_keys(passw)

time.sleep(2)

login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
login_button.click()

time.sleep(8)

# Navigate to Instagram Direct Messages (DMs)
driver.get('https://www.instagram.com/direct/inbox/')
time.sleep(5)

try:
    alert = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]')))
    alert.click()
except:
    pass

# Step 1: Open chat list and process each chat
chat_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x13dflua.x19991ni')))
print(f"Found {len(chat_divs)} chats.")

path = os.path.join(os.getcwd(), "Chats_" + u_name)
os.makedirs(path, exist_ok=True)

pdf_filename = "chats_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = 30

c.setFont("Times-Roman", 36)
c.drawCentredString(width / 2, height - 100, "INSTAGRAM CHATS")
c.setFont("Times-Roman", 32)
c.drawCentredString(width / 2, height - 140, f"{u_name}")
c.showPage()

def scale_image(img, max_width, max_height):
    img_width, img_height = img.size
    aspect_ratio = img_height / img_width

    if img_width > max_width:
        img_width = max_width
        img_height = img_width * aspect_ratio

    if img_height > max_height:
        img_height = max_height
        img_width = img_height / aspect_ratio

    return img_width, img_height

# Step 2: Process each chat, take screenshots, and add to PDF
for index, chat_div in enumerate(chat_divs):
    try:
        # Open the chat
        chat_button = chat_div.find_element(By.CSS_SELECTOR, 'div[role="button"]')
        chat_button.click()
        time.sleep(5)

        screenshot_path = os.path.join(path, f"chat_{index+1}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for chat {index+1}.")

        # Add screenshot to the PDF
        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        c.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        c.showPage()

    except Exception as e:
        print(f"Error processing chat {index+1}: {e}")
        continue

# Finalize and save the PDF
c.save()

# Close the browser
driver.quit()
