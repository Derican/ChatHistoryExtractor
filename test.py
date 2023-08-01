import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions

options = AppiumOptions()
options.set_capability("platformName", "Android")
options.set_capability("platformVersion", "10")
options.set_capability("automationName", "uiautomator2")
options.set_capability("deviceName", "3EP0219423003283")
options.set_capability("appPackage", "com.android.settings")
options.set_capability("appActivity", ".Settings")
options.set_capability("noReset", True)

appium_server_url = 'http://localhost:4723'


class TestAppium(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=options)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_find_battery(self) -> None:
        el = self.driver.find_element(by=AppiumBy.XPATH,
                                      value='//*[@text="WLAN"]')
        el.click()


if __name__ == '__main__':
    unittest.main()