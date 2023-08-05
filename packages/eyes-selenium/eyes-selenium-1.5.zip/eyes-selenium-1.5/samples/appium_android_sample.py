from selenium import webdriver
from applitools.eyes import Eyes

Eyes.api_key = 'YOUR_API_KEY'

# Appium session configuration.
desired_capabilities = {'device': 'Android',
                        'version': '4.2',
                        'app': 'PATH_TO_APK_FILE',
                        'app-package': 'YOUR.PACKAGE',
                        'app-activity': '.YourActivity'}

# Assuming Appium is running on localhost.
driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_capabilities)
eyes = Eyes()
try:
    eyes.open(driver, 'Appium', 'Hello android')
    eyes.check_window('Opening screen')
    # Find a button/link with the text "Click me!" on it, and click it.
    driver.find_element_by_name('Click me!').click()
    eyes.check_window('First click')
    eyes.close()
finally:
    driver.quit()
    eyes.abort_if_not_closed()
