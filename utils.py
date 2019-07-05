import os, time, re, pickle

from langdetect import detect
from googletrans import Translator
from google.cloud import translate

from config import Config


class Utils(object):
        
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

    # Получение списка лендов для проверки
    @staticmethod
    def get_lands():
        try:
            with open('landings.txt', 'r', encoding='utf-8') as f:
                rows = [row for row in f]
                lands = []
                for row in rows:
                    row = row.replace('\n', '')
                    if ' ' in row:
                        tmp_array = row.split(' ')
                    else:
                        tmp_array = [row, Config.DEFAULT_TRACK_URL]
                        
                    lands.append(tmp_array)
                return lands
        except OSError:
            print('landings.txt не найден')

    @staticmethod
    def cookies_exist():
        if os.path.isfile(Config.COOKIES):
#            if time.time() - os.path.getmtime(Config.COOKIES) > 7200:
#                print('cookies устарели')
#                return False
#            else:
                return True
        else:
            print('cookies не найдены')
            return False

    def cookie_saver(self):
        print('создаю cookies')
        self.driver.get("https://leadrock.com/administrator")
        time.sleep(4)
#        try:
#            self.f_xp("//img[@src='theme/img/landing/burger.svg']").click()
#            time.sleep(1)
#            self.f_xp("(//button[contains(.,'Login')])[2]").click()
#        except:
#            self.f_xp("(//button[contains(.,'Login')])[1]").click()
        self.driver.find_element_by_id("LoginForm_username").send_keys(self.LEADROCK_LOGIN)
        self.driver.find_element_by_id("LoginForm_password").send_keys(self.LEADROCK_PASS)
        self.f_xp("//input[@id='checkbox-signup']").click()
        self.f_xp("//button[@type='submit'][contains(.,'Log in')]").click()
        time.sleep(2)
        with open(self.COOKIES,"wb") as f:
            pickle.dump(self.driver.get_cookies(), f)
        print('cookies созданы \n')


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