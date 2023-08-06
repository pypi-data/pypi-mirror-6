from selenium import webdriver
from applitools import logger
from applitools.logger import StdoutLogger
from applitools.eyes import Eyes

# import os
#os.environ['HTTPS_PROXY'] = "http://localhost:8888"

Eyes.api_key = 'YOUR_API_KEY'
driver = webdriver.Firefox()

logger.set_logger(StdoutLogger())
eyes = Eyes()
try:
    eyes.open(driver, "Python app", "applitools", {'width': 800, 'height': 600})
    driver.get('http://www.applitools.com')
    eyes.check_window("initial")

    pricing_element = driver.find_element_by_css_selector("li.pricing a")
    eyes.check_region_by_element(pricing_element, "pricing page")

    pricing_element.click()
    eyes.check_window("pricing page")

    driver.find_element_by_css_selector("li.contact-us a").click()
    eyes.check_window("contact us page")
    driver.find_element_by_class_name("input-name").send_keys("my name is what?")
    eyes.check_window("name input")
    eyes.close()
finally:
    driver.quit()
    eyes.abort_if_not_closed()
