import requests
import pickle
import time
from lxml import html as lxhtml
from lxml import etree
from urllib.parse import unquote
import html

# Проверка наличия лида в лидроке
# Открываем лидрок, грузим куки, ищем lead
def lead_check(self):
    time.sleep(5) #ждем появления лида в базе

    tree = self.get_source('https://leadrock.com/administrator/lead')
    lead = self.get_text(tree, "//td[contains(.,'%s') and contains(.,'%s')]" % (self.lead, self.LEAD_NAME))
    if lead:
        self.log("лид дошел")
    else:
        self.logBad("не удалось найти лид c телефоном %s" % self.lead)
        return False

    # Получаем данные лида, оставленные пользователем
    lead_data = self.get_text(tree, "//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[3]" % (self.lead, self.LEAD_NAME))
    lead_data = lead_data.split('\n')
    lead_data = [x for x in lead_data if x]
    for s in lead_data:
        if ('Подробнее' not in s) and ('More information' not in s):
            self.log('  %s' % s)

    # Получаем номер постбэка
    self.postback_id = self.get_text(tree, "//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[2]" % (self.lead, self.LEAD_NAME))

    # Получаем номер лида
    self.lead_id = self.get_text(tree, "//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[1]/span[1]" % (self.lead, self.LEAD_NAME))

    # Получаем сабы
    lead_data = self.get_text(tree, ".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[6]" % (self.lead, self.LEAD_NAME))
    lead_subs = lead_data.split('\n')[2]
    if 'subid ' not in lead_subs:
        lead_subs = lead_subs.split(', ')
        for sub in lead_subs:
            self.log('  %s' % sub)

    return True













    # try:
    #     # WebDriverWait(self.driver, 6).until(
    #     #     EC.presence_of_element_located((By.XPATH, "//td[contains(.,'%s') and contains(.,'%s')]" % (self.lead, self.LEAD_NAME))))
    #     self.f_xp("//td[contains(.,'%s') and contains(.,'%s')]" % (self.lead, self.LEAD_NAME))
    #     self.log("лид дошел")

    #     try:
    #         self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[3]/a[@class='more-info']" % (self.lead, self.LEAD_NAME)).click()
    #     except:
    #         pass
        
    #     lead_data = self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[3]" % (self.lead, self.LEAD_NAME)).text.split('\n')
    #     for s in lead_data:
    #         if ('Скрыть' not in s) and ('Less information' not in s):
    #             self.log('  %s' % s)


    #     try:
    #         self.f_xp(".//tr[td[contains(.,'%s')  and contains(.,'%s')]]/td[4]/i[contains(@class,'fa-spinner')]" % s(elf.lead, self.LEAD_NAME))
    #         self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[10]/a[contains(@class,'trash')]" % (self.lead, self.LEAD_NAME)).click()
    #         time.sleep(1)
    #         self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[4]/i[contains(@class,'fa-trash-o')]" % (self.lead, self.LEAD_NAME))
    #         self.log("лид отправлен в trash")
    #     except:
    #         #f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[9]/a[contains(@class,'hold')]")
    #         try:
    #             self.f_xp(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[4]/i[contains(@class,'fa-trash-o')]" % (self.lead, self.LEAD_NAME))
    #             self.log("лид уже в trash")
    #         except:
    #             self.logBad("не удалось отправить в trash лид c телефоном %s" % self.lead)
    # except:
    #     self.logBad("не удалось найти лид c телефоном %s" % self.lead)
    #     return False