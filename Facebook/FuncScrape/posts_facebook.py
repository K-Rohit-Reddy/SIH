import os
import time
import wget
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page  # Import title page function

def fetch_facebook_posts(driver, pdf_report, fb_username):
    """Fetches Facebook posts and adds them to the PDF report."""
    
    # Create folder for saving post images inside 'Data'
    data_folder = os.path.join("C:/Users/katik/Desktop/insta-to-pdf/py/Facebook/Data", f"Data_{fb_username}", "Posts")
    os.makedirs(data_folder, exist_ok=True)

    # Add title page for posts section
    create_title_page(pdf_report, "POSTS")

    # Go to Facebook feed
    feed_url = f"https://www.facebook.com/?filter=all&sk=h_chr"
    driver.get(feed_url)
    time.sleep(5)

    # Scroll to load more posts
    n_scrolls = 3
    for _ in range(n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    # Extract images from posts
    images = []
    div_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x10l6tqk.x13vifvy'))
    )

    for div in div_elements:
        image_elements = div.find_elements(By.TAG_NAME, 'img')
        for img in image_elements:
            img_url = img.get_attribute('src')
            images.append(img_url)

    print(f'Found {len(images)} images inside the specified div.')

    # Define margins and dimensions for the PDF
    width, height = A4
    margin = 50
    padding = 20
    image_width = (width - 3 * margin) / 2
    image_height = (height - 2 * margin - padding) / 2

    # Download images and add them to the PDF
    for counter, image_url in enumerate(images, start=1):
        try:
            # Download the image
            image_path = os.path.join(data_folder, f"post_{counter}.jpg")
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
            pdf_report.drawImage(image_path, x, y, width=img_pdf_width, height=img_pdf_height)

            # If two images are placed on a single page, create a new page
            if counter % 2 == 0:
                pdf_report.showPage()

        except Exception as e:
            print(f"Error processing post {counter}: {e}")
            continue

    print("Posts successfully added to PDF.")
