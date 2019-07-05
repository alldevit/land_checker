import time, pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Проверка наличия лида в лидроке
# Открываем лидрок, грузим куки, ищем lead
def lead_check(self):
    time.sleep(6)
    self.driver.get("https://leadrock.com/")
    cookies = pickle.load(open(self.COOKIES, "rb"))
    for cookie in cookies:
        self.driver.add_cookie(cookie)
    self.driver.get("https://leadrock.com/administrator/lead")

######## experimental ########
#
#    if ('Name: test<br>Phone: ' + str(self.lead) in self.driver.page_source):
#        print("ЛИД НАЙДЕН ЙО")
##############################

    try:
        WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(.,'%s') and contains(.,'%s')]" % (self.lead, self.LEAD_NAME))))
        self.log("лид дошел")

        try:
            self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[3]/a[@class='more-info']" % (self.lead, self.LEAD_NAME)).click()
        except:
            pass
        
        lead_info = self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[3]" % (self.lead, self.LEAD_NAME)).text.split('\n')
        for s in lead_info:
            if ('Скрыть' not in s) or ('Less information' not in s):
                self.log('  %s' % s)


        try:
            self.f_xp(".//tr[td[contains(.,'%s')  and contains(.,'%s')]]/td[4]/i[contains(@class,'fa-spinner')]" % s(elf.lead, self.LEAD_NAME))
            self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[10]/a[contains(@class,'trash')]" % (self.lead, self.LEAD_NAME)).click()
            time.sleep(1)
            self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[4]/i[contains(@class,'fa-trash-o')]" % (self.lead, self.LEAD_NAME))
            self.log("лид отправлен в trash")
        except:
            #f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[9]/a[contains(@class,'hold')]")
            try:
                self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[4]/i[contains(@class,'fa-trash-o')]" % (self.lead, self.LEAD_NAME))
                self.log("лид уже в trash")
            except:
                self.logBad("не удалось отправить в trash лид c телефоном %s" % self.lead)
    except:
        self.logBad("не удалось найти лид c телефоном %s" % self.lead)
        return False