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
u_name = "amma_500026"  # Update with your username
passw = "Test123@"  # Update with your password

username.clear()
password.clear()
username.send_keys(u_name)
password.send_keys(passw)

time.sleep(2)

login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
login_button.click()

time.sleep(8)

# Navigate to the Comments section
driver.get("https://www.instagram.com/your_activity/interactions/comments")  # Update this URL if needed
time.sleep(6)

# Create directory for saving screenshots
path = os.path.join(os.getcwd(), "Comments_" + u_name)
os.makedirs(path, exist_ok=True)

# Variable to keep track of the number of screenshots taken
screenshot_index = 0
scroll_pause_time = 5  # Adjust if needed

# Scrollable div and comment logic
scrollable_div = driver.find_element(By.XPATH, '//div[@data-bloks-name="bk.components.Collection"]')

# Initialize tracking of comments
last_comment_count = 0
no_new_comments_counter = 0  # Track when no new comments are found

while True:
    # Find the div containing the comments
    comments_container = driver.find_element(By.XPATH, '//div[@data-testid="comments_container_non_empty_state"]')
    comments = comments_container.find_elements(By.XPATH, './/div[@data-testid="post_collection_item"]')

    # Take a screenshot of the entire page
    screenshot_path = os.path.join(path, f"comments_screenshot_{screenshot_index}.png")
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")

    # Check if the number of comments has increased
    new_comment_count = len(comments)

    if new_comment_count > last_comment_count:
        last_comment_count = new_comment_count  # Update the last comment count
        no_new_comments_counter = 0  # Reset counter when new comments are found
    else:
        no_new_comments_counter += 1  # Increment when no new comments are found

    # Break if no new comments have appeared for 2 consecutive attempts
    if no_new_comments_counter >= 2:  # Adjust this threshold as needed
        print("No new comments found. Stopping scrolling.")
        break

    # Scroll down the div to load more comments
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    time.sleep(scroll_pause_time)
    screenshot_index += 1  # Increment the screenshot index for the next screenshot

# Create PDF
pdf_filename = "comments_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = 30

# Add title page to PDF
c.setFont("Times-Roman", 36)
c.drawCentredString(width / 2, height - 100, "COMMENTS")
text_width = c.stringWidth("COMMENTS", "Times-Roman", 36)
underline_x_start = (width - text_width) / 2
underline_y = height - 105
c.setLineWidth(1)
c.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
c.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
c.setFont("Times-Roman", 32)
c.drawCentredString(width / 2, height - 140, f"{u_name}")
c.showPage()

# Add all screenshots to the PDF, excluding the last one
for i in range(screenshot_index):  # Change here to skip the last screenshot
    img_path = os.path.join(path, f"comments_screenshot_{i}.png")
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