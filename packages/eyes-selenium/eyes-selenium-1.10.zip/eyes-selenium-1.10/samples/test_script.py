from selenium import webdriver
from applitools.errors import TestFailedError
from applitools.eyes import Eyes
import json
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
    # If the test passed, the results are "close"'s return value.
    tr = eyes.close()
except TestFailedError as e:
    # Extracting the test results from the exception
    tr = e.test_results
finally:
    driver.quit()
    eyes.abort_if_not_closed()

# Example: transforming the results into a json string
json_results = json.dumps(dict(steps=tr.steps, matches=tr.matches, mismatches=tr.mismatches,
                               missing=tr.missing))

# Do something with the json result...