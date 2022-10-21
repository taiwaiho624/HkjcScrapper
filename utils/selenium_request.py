from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox') 
driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)

driver.get("https://www.google.com")
print(driver.page_source.encode('utf-8'))
