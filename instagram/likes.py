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

# Function to scale the image
def scale_image(img, max_width, max_height):
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height

    if img_width > max_width or img_height > max_height:
        if aspect_ratio > 1:  # Wider than tall
            img_width = max_width
            img_height = int(max_width / aspect_ratio)
        else:  # Taller than wide
            img_height = max_height
            img_width = int(max_height * aspect_ratio)

    return img_width, img_height

# Set up WebDriver
service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get("http://www.instagram.com")

time.sleep(6)

# Log in to Instagram
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
u_name = ""  # Update with your username
passw = ""  # Update with your password

username.clear()
password.clear()
username.send_keys(u_name)
password.send_keys(passw)

time.sleep(2)

login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
login_button.click()

time.sleep(8)

# Navigate to the Likes section
likes_url = "https://www.instagram.com/your_activity/interactions/likes"  # Update this URL if needed
driver.get(likes_url)
time.sleep(6)

# Create directory for saving screenshots
path = os.path.join(os.getcwd(), "Likes_" + u_name)
os.makedirs(path, exist_ok=True)

# Initialize variable to keep track of the number of screenshots taken
screenshot_index = 0

# Take an initial screenshot before trying to find the scrollable div
screenshot_path = os.path.join(path, f"likes_screenshot_{screenshot_index}.png")
driver.save_screenshot(screenshot_path)
print(f"Initial screenshot saved at: {screenshot_path}")
screenshot_index += 1

# Scroll and take screenshots of likes in a loop
try:
    scrollable_div = driver.find_element(By.XPATH, '//div[@data-blocks-name="bk.components.Collection"]')

    while True:
        # Take a screenshot of the Likes overview page
        screenshot_path = os.path.join(path, f"likes_screenshot_{screenshot_index}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at: {screenshot_path}")
        screenshot_index += 1

        # Scroll down to load more likes
        prev_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight", scrollable_div)
        time.sleep(3)  # Wait for loading more likes

        # Check if we have reached the end of the scrollable content
        new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_scroll_height == prev_scroll_height:
            print("Reached the end of the likes.")
            break

except Exception as e:
    print(f"Error while scrolling and taking screenshots: {e}")

# Create PDF
pdf_filename = "likes_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = 30

# Add title page to PDF
c.setFont("Times-Roman", 36)
c.drawCentredString(width / 2, height - 100, "LIKES")
text_width = c.stringWidth("LIKED POSTS", "Times-Roman", 36)
underline_x_start = (width - text_width) / 2
underline_y = height - 105
c.setLineWidth(1)
c.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
c.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
c.setFont("Times-Roman", 32)
c.drawCentredString(width / 2, height - 140, f"{u_name}")
c.showPage()

# Add all screenshots to the PDF
for i in range(screenshot_index):
    img_path = os.path.join(path, f"likes_screenshot_{i}.png")
    img = Image.open(img_path)
    img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
    x = (width - img_pdf_width) / 2
    y = (height - img_pdf_height) / 2
    c.drawImage(img_path, x, y, width=img_pdf_width, height=img_pdf_height)
    c.showPage()

# Save the PDF
c.save()
print(f"PDF saved as: {pdf_filename}")

# Close the browser
driver.quit()
