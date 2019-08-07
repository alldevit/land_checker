from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


import requests
import pickle
import time
from lxml import html as lxhtml
from lxml import etree
from urllib.parse import unquote
import html
import re


def get_text(elem):
    text = str(etree.tostring(elem))
    text = re.sub(r'<br>|<br/>', '\n', text)
    unescaped_text = html.unescape(text)
    debited_text = re.sub(r'^b\'|\'$', '', unescaped_text)
    regex = re.compile('<.*?>')
    clean_text = re.sub(regex, '', debited_text)
    return clean_text


# Проверка наличия лида в лидроке
# Открываем лидрок, грузим куки, ищем lead
def lead_check(self):
    time.sleep(3)
    with open(self.COOKIES, 'rb') as f:
        cookies = pickle.load(f)
        c_dict = {}
        for cookie in cookies:
            c_dict[cookie['name']] = cookie['value']

    response = requests.get('https://leadrock.com/administrator/lead', cookies=c_dict)
    page_text = response.text
    tree = lxhtml.fromstring(page_text)

    leads = tree.xpath("//td[contains(.,'%s') and contains(.,'%s')]" % (self.lead, self.LEAD_NAME))


    if len(leads) > 0:
        self.log("лид дошел")
    else:
        self.logBad("не удалось найти лид c телефоном %s" % self.lead)
        return False



    lead_data = tree.xpath("//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[3]" % (self.lead, self.LEAD_NAME))
    lead_data = get_text(lead_data[0]).split('\n')
    for s in lead_data:
        if ('Подробнее' not in s) and ('More information' not in s):
            self.log('  %s' % s)

    lead_track = tree.xpath(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[2]" % (self.lead, self.LEAD_NAME))
    lead_track = get_text(lead_track[0])

    lead_data = tree.xpath(".//tr[td[contains(.,'%s') and contains(.,'%s')]]/td[6]" % (self.lead, self.LEAD_NAME))
    lead_data = get_text(lead_data[0])
    lead_subs = lead_data.split('\n')[2]
    if 'subid ' not in lead_subs:
        lead_subs = lead_subs.split(', ')
        for sub in lead_subs:
            self.log('  %s' % sub)













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