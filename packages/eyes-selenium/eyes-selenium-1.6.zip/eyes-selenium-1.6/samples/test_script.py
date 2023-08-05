from selenium import webdriver
from applitools.eyes import Eyes
# import os

# os.environ['HTTPS_PROXY'] = "http://localhost:8888"

Eyes.api_key = 'YOUR_API_KEY'
driver = webdriver.Firefox()
eyes = Eyes()
try:
    driver = eyes.open(driver, "Python app", "applitools", {'width': 800, 'height': 600})
    driver.get('http://www.applitools.com')
    eyes.check_window("initial")
    driver.find_element_by_css_selector("li.pricing a").click()
    eyes.check_window("pricing page")
    eyes.close()
finally:
    driver.quit()
    eyes.abort_if_not_closed()


