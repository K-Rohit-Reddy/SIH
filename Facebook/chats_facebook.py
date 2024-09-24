from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

chrome_options = Options()
chrome_options.add_argument("--disable-notifications")

# Setup WebDriver with the specified options
service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("http://www.facebook.com")

# Log in to Facebook
email = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
fb_email = ""  # Provide Facebook Email
fb_password = ""  # Provide Facebook Password

# Extract username from email
fb_username = fb_email.split('@')[0]

email.clear()
password.clear()
email.send_keys(fb_email)
password.send_keys(fb_password)

login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'login')))
login_button.click()

time.sleep(5)

# Go to the Facebook feed
messages_url = "https://www.facebook.com/messages/t/"
driver.get(messages_url)

# Scroll down to load more messages
previous_height = driver.execute_script("return document.body.scrollHeight")

# Initialize list to store chat links
chat_links = []

# Scroll until no more new messages are loaded
while True:
    # Wait for the messages to load
    time.sleep(2)

    # Find all divs with class "x78zum5 xdt5ytf" and data-virtualized="false"
    # Find all divs with class "x78zum5 xdt5ytf" that are inside a div with class "x1n2onr6"
    chat_divs = driver.find_elements(By.XPATH, '//div[contains(@class, "x1n2onr6")]//div[contains(@class, "x78zum5 xdt5ytf") and @data-virtualized="false"]')


    # Extract href from anchor tags within the chat divs
    for chat_div in chat_divs:
        anchors = chat_div.find_elements(By.TAG_NAME, 'a')
        for anchor in anchors:
            href = anchor.get_attribute('href')
            if href and href not in chat_links:  # Check if href is not empty
                chat_links.append(href)

    # Scroll down to load more messages
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")

    # Break the loop if no new messages are loaded
    if new_height == previous_height:
        break
    previous_height = new_height


# Create a folder for saving screenshots
path = os.path.join(os.getcwd(), "Chats_" + fb_username)
os.makedirs(path, exist_ok=True)

# Initialize PDF document
pdf_filename = "chats_" + fb_username + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4

# Define margins and padding
margin = 30
image_spacing = 20

# Iterate through each chat link, open it, and take screenshots
for index, chat_link in enumerate(chat_links):
    try:
        # Navigate to the chat link
        driver.get(chat_link)
        time.sleep(5)  # Wait for the chat to load

        # Take a screenshot of the chat
        chat_screenshot_path = os.path.join(path, f"chat_{index + 1}_screenshot.png")
        driver.save_screenshot(chat_screenshot_path)
        print(f"Screenshot saved for chat {index + 1}.")

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
        print(f"Error processing chat {index + 1}: {e}")
        continue

# Finalize and save the PDF
c.save()

# Close the browser
driver.quit()
