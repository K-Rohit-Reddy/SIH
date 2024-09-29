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

# Define paths and service
service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Navigate to Twitter login
driver.get("https://x.com/i/flow/login")

# Wait for username input and enter username
username_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
u_name = "Lorven197843"  # Enter your username here
username_input.clear()
username_input.send_keys(u_name)

# Click 'Next' button
next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
next_button.click()

# Wait for password input and enter password
password_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password")))
passw = "Test@123"  # Enter your password here
password_input.clear()
password_input.send_keys(passw)

# Click 'Login' button
login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]')))
login_button.click()

time.sleep(8)

# Go to the profile page
profile_url = f"https://x.com/{u_name}"
driver.get(profile_url)
time.sleep(5)

# Scroll down the page to load more tweets
n_scrolls = 2
for _ in range(n_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Find tweets in the timeline
tweets_section = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label]'))
)

tweets = tweets_section.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

# Store tweet links
tweet_links = []
for tweet in tweets:
    try:
        link = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute('href')
        if link and link not in tweet_links:
            tweet_links.append(link)
    except:
        continue

print(f"Found {len(tweet_links)} tweets.")

# Set up directory for screenshots
path = os.path.join(os.getcwd(), "Tweets_" + u_name)
os.makedirs(path, exist_ok=True)

# Create PDF document
pdf_filename = "tweets_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = 30

c.setFont("Times-Roman", 36)
c.drawCentredString(width / 2, height - 100, "TWEETS")
c.setFont("Times-Roman", 32)
c.drawCentredString(width / 2, height - 140, f"{u_name}")
c.showPage()

# Function to scale images for PDF
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

# Capture each tweet and save to PDF
for counter, tweet_link in enumerate(tweet_links, start=1):
    try:
        driver.get(tweet_link)
        time.sleep(3)

        # Take a screenshot of the tweet
        screenshot_path = os.path.join(path, f"tweet_{counter}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for tweet {counter}.")

        # Add screenshot to PDF
        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        c.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        c.showPage()

        # Handle more media inside the tweet, if any (like Instagram)

    except Exception as e:
        print(f"Error processing tweet {counter}: {e}")
        continue

# Save PDF and quit browser
c.save()
driver.quit()
