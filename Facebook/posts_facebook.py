from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import wget
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
feed_url = f"https://www.facebook.com/?filter=all&sk=h_chr"
driver.get(feed_url)

time.sleep(5)

# Scroll to load more images (increase n_scrolls for more images)
n_scrolls = 3
for _ in range(n_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Extract image URLs only inside div with class "x10l6tqk x13vifvy"
images = []
div_elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x10l6tqk.x13vifvy'))
)

for div in div_elements:
    image_elements = div.find_elements(By.TAG_NAME, 'img')  # Find all img tags inside the div
    for img in image_elements:
        img_url = img.get_attribute('src')
        images.append(img_url)

print(f'Found {len(images)} images inside the specified div.')

# Create folder for saving images
path = os.path.join(os.getcwd(), "FB_Posts_" + fb_username)
os.makedirs(path, exist_ok=True)

# Create a PDF for the images
pdf_filename = "FB_posts_" + fb_username + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4

# Define margins and spacing for the images in the PDF
margin = 50
padding = 20
image_width = (width - 3 * margin) / 2
image_height = (height - 2 * margin - padding) / 2

# Download images and add them to the PDF
for counter, image_url in enumerate(images, start=1):
    try:
        # Download the image
        image_path = os.path.join(path, f"fb_image_{counter}.jpg")
        wget.download(image_url, image_path)
        
        # Load the image to get its dimensions for scaling
        img = Image.open(image_path)
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width
        
        # Adjust the image size while maintaining the aspect ratio
        img_pdf_width = image_width
        img_pdf_height = img_pdf_width * aspect_ratio
        if img_pdf_height > image_height:
            img_pdf_height = image_height
            img_pdf_width = img_pdf_height / aspect_ratio

        # Calculate positions for two images per page
        if (counter - 1) % 2 == 0:
            x = margin
            y = height - margin - img_pdf_height
        else:
            x = width / 2 + margin / 2
            y = height / 2 - margin / 2

        # Draw the image onto the PDF
        c.drawImage(image_path, x, y, width=img_pdf_width, height=img_pdf_height)

        # If two images are placed on a single page, create a new page
        if counter % 2 == 0:
            c.showPage()

    except Exception as e:
        print(f"Error processing image {counter}: {e}")
        continue

# Save the final PDF document
c.save()

# Close the browser
driver.quit()
