import os
import sys
import time
import re
import pickle
import html
import requests
from lxml import html as lxhtml

from lxml import etree
from langdetect import detect
from googletrans import Translator
from google.cloud import translate

from config import Config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException


class Utils(object):

    @staticmethod
    def turn_off(message=''):
        if message:
            print(message)        
        input('Press ENTER to exit\n')
        sys.exit(0)
    
    @staticmethod
    def self_check():
        errors = []

        try:
            x = Driver()
        except SessionNotCreatedException:
            errors.append('вероятно, версия chromedriver устарела')

        if not hasattr(Config, 'INPUT_FILE'):
            errors.append('в config.py не найден параметр INPUT_FILE')
        elif not os.path.isfile(Config.INPUT_FILE):
            errors.append('не найден %s' % Config.INPUT_FILE)
        if not hasattr(Config, 'SERVER_LOGIN'):
            errors.append('в config.py не найден параметр SERVER_LOGIN')
        if not hasattr(Config, 'SERVER_PASS'):
            errors.append('в config.py не найден параметр SERVER_PASS')
        if not os.path.isfile(Config.DRIVER_PATH):
            errors.append('не найден %s' % Config.DRIVER_PATH)
        if not os.path.isfile(Config.GJSON):
            errors.append('не найден %s' % Config.GJSON)
        if 'логин' in Config.SERVER_LOGIN:
            errors.append('не указан логин для приватного сервера')
        if 'пароль' in Config.SERVER_PASS:
            errors.append('не указан пароль для приватного сервера')
        if errors:
            for error in errors:
                print(error)
            Utils.turn_off()
        
        
    # Сокращение стандартных методов WebDriver
    def f_xp(self, s):
        return self.driver.find_element_by_xpath(s)
    def f_xps(self, s):
        return self.driver.find_elements_by_xpath(s)
    def f_tag(self, s):
        return self.driver.find_element_by_tag_name(s)
    def f_tags(self, s):
        return self.driver.find_elements_by_tag_name(s)

    # логирование -
    def logBad(self, text):
        text = '- ' + str(text) + '\n'
        print(text[:-1])
        try:
            self.log_bad_list.append(text[:-1])
        except:
            pass
        with open(self.LOG_LATEST, 'a', encoding='utf-8') as f:
            f.write(text)
        with open(self.LOG_FULL, 'a', encoding='utf-8') as f:
            f.write(text)

    # логирование +
    def log(self, text, force=False):
        text = '  ' + str(text)
        if force or (not Config.SILENT_MODE and not force):
            print(text)
            with open(self.LOG_LATEST, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
        with open(self.LOG_FULL, 'a', encoding='utf-8') as f:
            f.write(text + '\n')

    # Сравнение языков элементов и вывод результата сравнения
    def compare(self, page_lang, elem_lang, elem):
        if elem_lang != 'en':
            if page_lang == elem_lang:
                self.log('язык %s (%s) совпадает с языком страницы (%s)' % (elem, elem_lang, page_lang))
            else:
                self.logBad('язык %s (%s) не совпадает с языком страницы (%s)' % (elem, elem_lang, page_lang))
        else:
            self.log('язык %s (%s) совпадает с языком страницы (%s)' % (elem, elem_lang, page_lang))

    # Открытие ссылки
    def page_open(self, url):
        self.driver.get(url)
        time.sleep(1)

    # Закрытие webdriver
    def stop(self):
        self.driver.quit()

    # Чистка повторяющихся пробелов и цифр
    @staticmethod
    def cleaner(s):
        return re.sub(r'\s+', ' ', re.sub(r'\d+', '', s))

    # Деуникализатор текста
    @staticmethod
    def replacer(s):
        trans_table = str.maketrans('аеосрхАЕОСРХ','aeocpxAEOCPX')
        return s.translate(trans_table)

    # Удаление последнего лога
    @staticmethod
    def log_restart():
        try:
            os.remove(Config.LOG_LATEST)
        except OSError:
            pass

    # Получение исходного текста страницы через requests
    def get_source(self, link):
        response = requests.get(link, cookies=self.cookie_dict)
        page_text = response.text
        tree = lxhtml.fromstring(page_text)
        return tree

    # Получение текста из lxml-элемента
    @staticmethod
    def get_text(tree, xp):
        elem = tree.xpath(xp)
        if len(elem) > 0:
            text = str(etree.tostring(elem[0]))
            text = re.sub(r'<br>|<br/>', '\n', text)
            unescaped_text = html.unescape(text)
            debyted_text = re.sub(r'^b\'|\'$', '', unescaped_text)
            regex = re.compile('<.*?>')
            clean_text = re.sub(regex, '', debyted_text)
            return clean_text
        else:
            return False

    # Получение списка лендов для проверки
    @staticmethod
    def get_lands():
        with open(Config.INPUT_FILE, 'r', encoding='utf-8') as f:
            rows = [row for row in f]
            lands = []
            for row in rows:
                row = re.sub(r'\n|^\s+|\s+$', '', row)
                row = re.sub(r'\s+', ' ', row)
                if 'http' in row:
                    if ' ' in row:
                        tmp_array = row.split(' ')
                    else:
                        tmp_array = [row, Config.DEFAULT_TRACK_URL]
                    
                lands.append(tmp_array)
            if lands:
                return lands
            else:
                Utils.turn_off('в %s не обнаружено корректных ссылок' % Config.INPUT_FILE)

    @staticmethod
    def cookies_exist():
        if os.path.isfile(Config.COOKIES):
            return True
        else:
            print('cookies не найдены')
            return False

    def cookie_saver(self):
        print('для создания cookies, пожалуйста, авторизуйтесь')
        self.driver.get("https://leadrock.com/")

        while True:
            time.sleep(2)
            if 'administrator' in self.driver.current_url:
                with open(self.COOKIES,"wb") as f:
                    pickle.dump(self.driver.get_cookies(), f)
                print('cookies созданы \n')
                break


class Lang(object):

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GJSON

    def lang_detect_page(self, text):
        if len(Utils.replacer(text)) > 1:
            lang = Lang.detect_lib(text)[:2]
            if lang not in 'ru, bg':
                lang = Lang.detect_lib(Utils.replacer(text))
            self.lang = lang
            return lang
        else:
            print('на странице нет текста')
            return 'error'

    def lang_detect(self, text, method='lib'):
        detect_methods = {'lib':Lang.detect_lib, 'cloud':Lang.detect_cloud, 'api':Lang.detect_api}
        if len(Utils.replacer(text)) > 1:
            if str(self.lang) not in 'ru, bg':
                lang = detect_methods[method](Utils.cleaner(Utils.replacer(text)))[:2]
            else:
                lang = detect_methods[method](Utils.cleaner(text))[:2]
            return lang
        else:
            return 'error'


    def lang_translate(self, text, method):
        translate_methods = {'lib':Lang.translate_lib, 'cloud':Lang.translate_cloud, 'api':Lang.translate_api}
        if self.lang == 'ru':
            translated = text
        elif self.lang == 'bg':
            try:
                translated = translate_methods[method](Utils.cleaner(text))
            except:
                translated = 'ERROR'
        else:
            try:
                translated = translate_methods[method](Utils.cleaner(Utils.replacer(text)))
            except:
                translated = 'ERROR'
        return translated

    @staticmethod
    def detect_lib(s):
        return detect(s)

    @staticmethod
    def translate_lib(s):
        return s

    @staticmethod
    def detect_cloud(s):
        client = translate.Client()
        detected = client.detect_language(s)
        return detected['language']

    @staticmethod
    def translate_cloud(s):
        translate_client = translate.Client()
        translated = translate_client.translate(s, 'ru')
        return translated['translatedText']

    @staticmethod
    def detect_api(s):
        time.sleep(0.5)
        translator = Translator()
        detected = translator.detect(s[:5000])
        return getattr(detected, 'lang')[:2]

    @staticmethod
    def translate_api(s):
        text_array = [s[i:i+4500] for i in range(0,len(s),4500)]
        translated = ''
        for s in text_array:
            time.sleep(0.5)
            translator = Translator()
            g_query = translator.translate((s), dest='ru')
            translated = translated + getattr(g_query, 'text')
        return translated


class Driver(Config, Utils, Lang):
    def __init__(self, images=False, headless=True):
        options = Options()
        options.add_argument('log-level=2')
        options.add_argument("--start-maximized")
        options.add_argument('--incognito')
        if self.HEADLESS_MODE and headless:
            options.add_argument('--headless')
        if not images:
            prefs = {'profile.managed_default_content_settings.images':2}
            options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(self.DRIVER_PATH, options=options)
        self.driver.delete_all_cookies()
        self.log_bad_list = []

        try:
            with open(self.COOKIES, 'rb') as f:
                cookies = pickle.load(f)
                c_dict = {}
                for cookie in cookies:
                    c_dict[cookie['name']] = cookie['value']
            self.cookie_dict = c_dict
        except:
            pass