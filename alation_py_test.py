#!/usr/bin/python
# @author Alfredo

import os
import sys
import new
import unittest
from selenium import webdriver
from sauceclient import SauceClient
# it's best to remove the hardcoded defaults and always get these values
# from environment variables but harcoding for test completion
# USERNAME = os.environ['USERNAME']
# ACCESS_KEY = os.environ['ACCESS_KEY']
USERNAME = "norbak"
ACCESS_KEY = "c599d22a-51aa-4655-9348-5c1e48ea0698"
email_text = "devops@alation.com"
password_text = "hHe3k7Lla7zuvKqhbemG"
sauce = SauceClient(USERNAME, ACCESS_KEY)
browsers = [{"platform": "OS X 10.9",
             "browserName": "firefox",
             "version": "45.0"},
            {"platform": "Windows 8.1",
             "browserName": "chrome",
             "version": "43"}
            ]
 
def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)
    return decorator
 
@on_platforms(browsers)
class AlationSmokeTest(unittest.TestCase):
    def setUp(self):
        self.desired_capabilities['name'] = self.id()
        sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor=sauce_url % (USERNAME, ACCESS_KEY)
        )
        self.driver.implicitly_wait(30)
    def test_login(self):
        self.driver.get('https://alfredo.trialalation.com')
        assert "Alation" in self.driver.title
        
        email = self.driver.find_element_by_id("email")
        email.send_keys(email_text)
        password = self.driver.find_element_by_id('password')
        password.send_keys(password_text)
        self.driver.find_element_by_xpath("//button[contains(.,'Sign In')]").click()
        self.driver.implicitly_wait(10)
        assert "Welcome to Alation | Alation" in self.driver.title
    def tearDown(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
        try:
            if sys.exc_info() == (None, None, None):
                sauce.jobs.update_job(self.driver.session_id, passed=True)
            else:
                sauce.jobs.update_job(self.driver.session_id, passed=False)
        finally:
            self.driver.quit()
 
if __name__ == '__main__':
    unittest.main()
    
