from selenium import webdriver
from applitools.eyes import Eyes

Eyes.api_key = 'YOUR_API_KEY'
driver = webdriver.Firefox()
eyes = Eyes()
try:
    eyes.open(driver, "Python app", "applitools", {'width': 800, 'height': 600})
    driver.get('http://www.applitools.com')
    eyes.check_window("Home Page")
    driver.find_element_by_css_selector('read_more').click()
    eyes.check_window("Features Page")
    eyes.close()
finally:
    driver.quit()
    eyes.abort_if_not_closed()


