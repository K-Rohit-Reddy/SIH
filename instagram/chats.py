from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image

# Setup WebDriver
service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get("http://www.instagram.com")

time.sleep(6)

# Log in to Instagram
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
u_name = "amma_500026"  # Provide Instagram Username
passw = "Test123@"  # Provide Instagram Password
username.clear()
password.clear()
username.send_keys(u_name)
password.send_keys(passw)

time.sleep(2)

login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
login_button.click()

time.sleep(5)

# Handle alerts (e.g., "Not Now" for saving login info)
try:
    alert = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]')))
    alert.click()
except:
    pass

time.sleep(8)

### Navigate to Instagram Direct Messages (DMs) ###
driver.get('https://www.instagram.com/direct/inbox/')
time.sleep(5)

try:
    alert = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]')))
    alert.click()
except:
    pass


### Step 1: Find all divs representing chats ###
chat_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x13dflua.x19991ni')))
print(f"Found {len(chat_divs)} chats.")

### Create folder for saving screenshots ###
path = os.path.join(os.getcwd(), "Chats_"+u_name)
os.makedirs(path, exist_ok=True)

# Initialize PDF document
pdf_filename = "chats_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4

# Define margins and padding
margin = 30
image_spacing = 20

### Step 2: Iterate through each chat, click and take screenshots ###
for index, chat_div in enumerate(chat_divs):
    try:
        # Find the button inside each chat div and click to open the chat
        chat_button = chat_div.find_element(By.CSS_SELECTOR, 'div[role="button"]')
        chat_button.click()
        time.sleep(5)  # Wait for the chat to load

        # Take a screenshot of the chat
        chat_screenshot_path = os.path.join(path, f"chat_{index+1}_screenshot.png")
        driver.save_screenshot(chat_screenshot_path)
        print(f"Screenshot saved for chat {index+1}.")

        ### Add screenshot to the PDF ###
        # Open the screenshot to get its size and aspect ratio
        img = Image.open(chat_screenshot_path)
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width

        # Calculate the image size for the PDF, keeping aspect ratio intact
        img_pdf_width = width - 2 * margin
        img_pdf_height = img_pdf_width * aspect_ratio

        # If the image height is greater than the available space, adjust the width and height
        if img_pdf_height > (height - 2 * margin):
            img_pdf_height = height - 2 * margin
            img_pdf_width = img_pdf_height / aspect_ratio

        # Calculate position to center the image
        x = (width - img_pdf_width) / 2
        y = height - margin - img_pdf_height - ((index % 2) * (img_pdf_height + image_spacing))

        # Draw the image on the PDF
        c.drawImage(chat_screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)

        # Add a new page every 1 image (or adjust if you'd like multiple per page)
        if (index + 1) % 1 == 0:
            c.showPage()

    except Exception as e:
        print(f"Error processing chat {index+1}: {e}")
        continue

### Finalize and save the PDF ###
c.save()

# Close the browser
driver.quit()