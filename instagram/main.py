from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import shutil

from FuncScrape.saved import fetch_saved_posts
from FuncScrape.tagged import fetch_tagged_posts
from FuncScrape.posts import fetch_posts
from FuncScrape.comments import fetch_comments
from FuncScrape.likes import fetch_likes
from FuncScrape.chats import fetch_chats

def create_data_folder(username):
    folder_name = f"Data_{username}"
    folder_path = os.path.join("instagram","Data", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created directory: {folder_path}")
    else:
        print(f"Directory already exists: {folder_path}")

def create_title_page(username, pdf_report):
    width, height = A4
    pdf_report.setFont("Times-Roman", 50)
    title_y = height / 2 + 50
    pdf_report.drawCentredString(width / 2, title_y, "Instagram Report")
    text_width = pdf_report.stringWidth("Instagram Report", "Times-Roman", 50)
    underline_x_start = (width - text_width) / 2
    underline_y = title_y - 5
    pdf_report.setLineWidth(1)
    pdf_report.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
    pdf_report.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
    pdf_report.setFont("Times-Roman", 32)
    username_y = title_y - 50
    pdf_report.drawCentredString(width / 2, username_y, f"Username: {username}")
    pdf_report.showPage()

def login_instagram(driver, username, password):
    driver.get("http://www.instagram.com")
    time.sleep(6)
    user_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    pass_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    user_input.clear()
    pass_input.clear()
    user_input.send_keys(username)
    pass_input.send_keys(password)
    time.sleep(2)
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    time.sleep(8)
    print(f"Logged in as {username}")

def compile_report(username, password):
    create_data_folder(username)
    report_filename = os.path.join("instagram","Data",f"Data_{username}", f"Instagram_Report.pdf")
    pdf_report = canvas.Canvas(report_filename, pagesize=A4)
    create_title_page(username, pdf_report)
    driver = webdriver.Chrome()
    driver.maximize_window()
    login_instagram(driver, username, password)
    fetch_posts(driver, pdf_report, username)
    fetch_chats(driver, pdf_report, username)
    fetch_comments(driver, pdf_report, username)
    fetch_likes(driver, pdf_report, username)
    fetch_saved_posts(driver, pdf_report, username)
    fetch_tagged_posts(driver, pdf_report, username)
    pdf_report.save()
    print(f"Instagram report saved as: {report_filename}")
    driver.quit()

if __name__ == "__main__":
    u_name = input("Enter Instagram username: ")
    passw = input("Enter Instagram password: ")
    compile_report(u_name, passw)
    pycache_dir = os.path.join(os.getcwd(),'instagram','FuncScrape', '__pycache__')
    if os.path.exists(pycache_dir):
        shutil.rmtree(pycache_dir)
        print(f"Deleted {pycache_dir} directory.")
    else:
        print(f"{pycache_dir} directory does not exist.")

