import requests
import pickle
import time
from lxml import html as lxhtml
from lxml import etree
import re

def postback(self):
    if self.track_url == self.DEFAULT_TRACK_URL:
        self.get_source('https://leadrock.com/administrator/lead/hold/id/%s' % self.lead_id)
        time.sleep(3)
        tree = self.get_source('https://leadrock.com/administrator/postback/index/CHPostbackLog[track_id]/%s' % self.postback_id)
        postback = self.get_text(tree, "//tr[contains(@class, 'odd')]/td[7]")
        self.get_source('https://leadrock.com/administrator/lead/trash/id/%s' % self.lead_id)
        if postback:
            if ('{' or '}') in postback:
                self.logBad('в постбэке %s есть фигурные скобки' % self.postback_id)
                print(postback)
            else:
                self.log('постбэк корректен')

            advert_response = self.get_text(tree, "//td[contains(@class, 'postback-response')][1]")
            if (advert_response == '""') or \
                ('\\"answer\\":\\"ok\\"' in advert_response) or \
                (advert_response == re.sub(r'\D', '', advert_response)):
                    self.log('ответ рекламодаеля корректен')
            else:
                self.log('ответ рекла:\n  %s' % advert_response)
        else:
            self.logBad('постбэки лида %s не найдены' % self.lead_id)
            return False