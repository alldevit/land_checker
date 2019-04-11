import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from checker_config import *



def cookie_saver():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(driver_path, options=options)

################# Авторизационные данные #####################
    email = "email@leadrock.com"
    password = "password"
##############################################################

    # проверка наличия лида в лидроке
    driver.get("https://leadrock.com/administrator")
    time.sleep(3)
    try:
        driver.find_element_by_xpath("//img[@src='dist/img/bars.png']").click()
    except ElementNotVisibleException:
        pass

    driver.find_element_by_xpath("(//a[@class='show-modal'])[1]").click()
    driver.find_element_by_id("LoginForm_username").send_keys(email)
    driver.find_element_by_id("LoginForm_password").send_keys(password)
    driver.find_element_by_xpath("//input[@data-parsley-multiple='LoginFormrememberMe']").click()
    driver.find_element_by_xpath("//button[contains(.,'Log in')]").click()
    time.sleep(2)
#    driver.get("https://leadrock.com/administrator/lead?Lead%5Boffer_id%5D%5B%5D=301")
#    pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
    with open("cookies.pkl","wb") as f:
        pickle.dump(driver.get_cookies(), f)


cookie_saver()