# Установка базовых модулей:
# python -m pip install --upgrade pip
# pip install selenium langdetect requests
#
# Установка дополнительных модулей для расширенной работы с переводом:
# pip install googletrans google-cloud-translate pickle

import sys, os, time, random, requests, logging, re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from langdetect import detect
from langdetect import detect_langs
#from googletrans import Translator
#from google.cloud import translate
import pickle

########################## НАСТРОЙКИ ###############################
track_url = "URL-C53EA-0260C"#трек-урл с левого оффера, нужен в служебных целях
fbpixel = "123123123123"
driver_path = "C:/Users/ed/testing/chromedriver/chromedriver.exe"
mini_log = "mini.log"
full_log = "full.log"
lang_log = "lang.log"
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/ed/testing/check_landings/g.json"
####################################################################


def logBad(text):
    text = '- ' + str(text) + '\n'
    print(text[:-1])
    with open(mini_log, "a", encoding="utf-8") as f:
        f.write(text)

def log(text):
    print("  " + str(text))
    with open(mini_log, "a", encoding="utf-8") as f:
        f.write("  " + str(text) + "\n")

def compare(page_lang, elem_lang, elem):
    if elem_lang!="en":
        if page_lang == elem_lang:
            log("язык " + elem + " совпадает с языком страницы " + elem_lang)
        else:
            logBad("язык " + elem + " не совпадает с языком страницы " + elem_lang)
    else:
        log("язык " + elem + " совпадает с языком страницы " + elem_lang)

def replacer(s):
    global lang
    if lang != "ru" and lang != "bg":
        s = s.replace("а", "a")
        s = s.replace("е", "e")
        s = s.replace("о", "o")
        s = s.replace("с", "c")
        s = s.replace("р", "p")
        s = s.replace("х", "x")
        s = s.replace("А", "A")
        s = s.replace("Е", "E")
        s = s.replace("О", "O")
        s = s.replace("С", "C")
        s = s.replace("Р", "P")
        s = s.replace("Х", "X")
    return s

def land_open():
    driver.get(link)
    time.sleep(1)

def log_add():
    try:
        with open(mini_log, "r", encoding="utf-8") as f:
            txt = f.read()
        with open(full_log, "a", encoding="utf-8") as f:
            f.write(txt)
        os.remove(mini_log)
    except OSError:
        pass

############## перевод библиотекой ###############
def lang_detect(text):
    global lang
    if 'lang' not in globals():
        lang = detect(cleaner(text))
        if lang != "ru" and lang != "bg":
            lang = detect(cleaner(replacer(text)))
        log(lang)
        return lang
    else:
        if lang != "ru" and lang != "bg":
            local_lang = detect(cleaner(replacer(text)))
        else:
            local_lang = detect(cleaner(text))
        return local_lang

def lang_translate(text):
    return text

############## перевод через облако ##############
#def lang_detect(text):
#    global lang
#    client = translate.Client()
#    if 'lang' not in globals():
#        g_query = client.detect_language(cleaner(text)[:4500])
#        lang = g_query["language"]
#        log(lang)
#        return lang
#    else:
#        g_query = client.detect_language(cleaner(replacer(text))[:4500])
#        local_lang = g_query["language"]
#        return local_lang
#
#def lang_translate(text):
#    global lang
#    if lang != "ru":
#        translate_client = translate.Client()
#        g_query = translate_client.translate(cleaner(replacer(text)), "ru")
#        translated = g_query["translatedText"]
#        return translated
#    else:
#        return text

############### перевод через API ################
#def lang_detect(text):
#    global lang
#    translator = Translator()
#    if 'lang' not in globals():
#        g_query = translator.detect(cleaner(text)[:4500])
#        lang = getattr(g_query, "lang")[:2]
#        log(lang)
#        return lang
#    else:
#        g_query = translator.detect(cleaner(replacer(text))[:4500])
#        local_lang = getattr(g_query, "lang")[:2]
#        return local_lang
#
#def lang_translate(text):
#    global lang
#    if lang != "ru":
#        translator = Translator()
#        g_query = translator.translate(cleaner(replacer(text))[:5000], dest="ru")
#        translated = getattr(g_query, "text")
#        return translated
#    else:
#        return text
#
#def lang_translate2(text):
#    global lang
#    if lang != "ru":
#        text_array = [text[i:i+4500] for i in range(0,len(text),4500)]
#        translated = ""
#        translator = Translator()
#        for s in text_array:
#           g_query = translator.translate(cleaner(replacer(s)), dest="ru")
#           translated = translated + getattr(g_query, "text")
#        return translated
#    else:
#        return text

def cleaner(s):
    return re.sub(r'\s+', ' ', re.sub(r"\d+", "", s))

# определение языка ленда
def test_global_lang():
    global lang
    text = driver.find_element_by_tag_name("body").text
    lang_detect(text)
    return lang

# определение языка каждого элемента
def test_elements_lang():
    if lang != "ru":
        source_text = replacer(driver.find_element_by_tag_name("body").text)
        with open(lang_log, "a", encoding="utf-8") as kek:
            kek.write("\n" + land + "\n")
        strings = source_text.split("\n")
        lang_error = 0
        for s in strings:
            st = cleaner(s)
            if len(st) > 20:
                lang_s = lang_detect(st[:1000])
                print('.',sep='', end='', flush=True)
                if (lang != lang_s) and (lang_s != "en"):
                    with open(lang_log, "a", encoding="utf-8") as kek:
                        kek.write(lang_s + " is not " + lang + " " + s + "\n")
                    lang_error += 1
        print("")
        if lang_error > 0:
            logBad("возможное несовпадение языка " + str(lang_error) + " элементов")
    


# проверка доступности ленда
def test_available():
    response = str(requests.head(link))
    if "500" in response:
        logBad("ленд недоступен - 500")
        return False
    elif "No input file specified" in driver.page_source:
        logBad("ленд недоступен")
        return False
    else:
        return True

# проверка наличия title и его языка
def test_title():
    try:
        title = driver.find_element_by_tag_name("title")
        log("title существует")
        lang_title = lang_detect(title.get_attribute('innerHTML'))
        compare(lang, lang_title, "title")
        return True
    except NoSuchElementException:
        logBad("title отсутствует")
        return False

# проверка языка description и keywords
def test_meta_lang(name):
    try:
        elem = driver.find_element_by_xpath("//meta[@name='" + name + "']")
        if len(elem.get_attribute("content")) > 0:
            lang_elem = lang_detect(elem.get_attribute("content"))
            compare(lang, lang_elem, name)
    except NoSuchElementException:
        pass

# проверка наличия юрлица
def test_contacts():
    if "GERARDE" in replacer(driver.page_source):
        log("юрлицо на месте")
        return True
    else:
        logBad("юрлицо не указано")
        return False

# проверка наличия линка на политику
def test_policy_link():
    try:
        driver.find_element_by_xpath("//a[contains(@href,'policy')]")
        log("ссылка на policy на месте")
        return True
    except NoSuchElementException:
        logBad("ссылка на policy отсутствует")
        return False

# проверка открытия политики в новой вкладке
def test_policy_blank():
    try:
        driver.find_element_by_xpath("//a[contains(@href,'policy') and @target='_blank']")
        log("policy открывается в новой вкладке")
        return True
    except NoSuchElementException:
        logBad("policy не открывается в новой вкладке")
        return False

# проверка доступности политики
def test_policy_available():
    driver.get(driver.find_element_by_xpath("//a[contains(@href,'policy')]").get_attribute("href"))
    try:
        driver.find_element_by_xpath('//*[contains(text(), "No input file specified")]')
        logBad("файл policy недоступен")
    except NoSuchElementException:
        log("файл policy на месте")

# проверка языка политики
def test_policy_lang():
    lang_policy = lang_detect(driver.find_element_by_tag_name("body").text)
    compare(lang, lang_policy, "policy")

# проверка существования спасибо
def test_thankyou():
    driver.get(land + "/thankyou.php")
    try:
        driver.find_element_by_xpath('//*[contains(text(), "No input file specified")]')
        driver.get(land + "/confirm.html")
        try:
            driver.find_element_by_xpath('//*[contains(text(), "No input file specified")]')
            logBad("страница thankyou недоступна")
        except NoSuchElementException:
            log("страница thankyou доступна")
            lang_thankyou = lang_detect(driver.find_element_by_tag_name("body").text)
            compare(lang, lang_thankyou, "thankyou")
    except NoSuchElementException:
        log("страница thankyou доступна")
        lang_thankyou = lang_detect(driver.find_element_by_tag_name("body").text)
        compare(lang, lang_thankyou, "thankyou")

# проверка упоминания почты в тексте
def test_shipping_post():
    source_text = driver.find_element_by_tag_name("body").text.lower()
    if lang == "ru":
        if "почт" in source_text:
            logBad("в тексте упоминается почта")
    else:
        source_text_ru = lang_translate(source_text)
        if "почт" in source_text_ru:
            logBad("в тексте упоминается почта")
            with open("pochta.log", "a", encoding="utf-8") as f:
                f.write(source_text_ru)

# проверка форм на POST
def test_post_forms():
    post_num = len(driver.find_elements_by_xpath("//form[@method='POST' or @method='post']"))
    form_num = len(driver.find_elements_by_tag_name("form"))
    if form_num == post_num:
        log("все формы отправляются через POST")
        return True
    else:
        logBad("не все формы отправляются через POST")
        return False

# проверка наличия GET форм
def test_get_forms():
    try:
        driver.find_element_by_xpath("//form[@method='GET' or @method='get']")
        logBad("на странице есть формы, отправляемые через GET")
        return False
    except NoSuchElementException:
        return True

# проверка наличия submit
def test_submit():
    form_num = len(driver.find_elements_by_tag_name("form"))
    submit_num = len(driver.find_elements_by_xpath("//*[@type='submit']"))
    if form_num == submit_num:
        log("во всех формах есть кнопка submit")
        return True
    else:
        logBad("в форме(ах) пропущена кнопка submit")
        return False

# проверка required для поля
def test_required(elem):
    elem_num = len(driver.find_elements_by_xpath("//input[@name='" + elem + "']"))
    elem_req_num = len(driver.find_elements_by_xpath("//input[@name='" + elem + "' and @required]"))
    if elem_num == elem_req_num:
        log("для всех " + elem + " установлен required")
        return True
    else:
        logBad("для " + elem + " не установлен required")
        return False

# проверка наличия fbpixel
def test_fbpixel_main():
    if "fbq('init', '123123123123')" in driver.page_source:
        log("fbpixel работает")
        return True
    else:
        logBad("fbpixel не работает")
        return False

# проверка наличия коллбэка
def test_callback():
    try:
        driver.find_element_by_class_name("callback-btn").is_displayed()
        log("коллбэк на месте")
        return True
    except NoSuchElementException:
        try:
            driver.find_element_by_class_name("feedback").is_displayed()
            log("коллбэк на месте")
            return True
        except NoSuchElementException:
            logBad("коллбэк остутствует")
            return False

# отправка лида
def test_lead():

    req_num = len(driver.find_elements_by_xpath("//input[@required]"))
    for i in range(1, req_num + 1):
        try:
            driver.find_element_by_xpath("(//input[@required])[" + str(i) + "]").send_keys("1")
        except:
            pass

    phone_num = len(driver.find_elements_by_xpath("//input[@name='phone' and @required]"))
    for i in range(1, phone_num + 1):
        try:
            driver.find_element_by_xpath("(//input[@name='phone' and @required])[" + str(i) + "]").send_keys(lead)
        except:
            pass

    name_num = len(driver.find_elements_by_xpath("//input[@name='name' and @required]"))
    for i in range(1, name_num + 1):
        try:
            driver.find_element_by_xpath("(//input[@name='name' and @required])[" + str(i) + "]").send_keys("test")
        except:
            pass
    
    submit_num = len(driver.find_elements_by_xpath("//*[@type='submit']"))
    for i in range(1, submit_num + 1):
        try:
            driver.find_element_by_xpath("(//*[@type='submit'])[" + str(i) + "]").click()
        except:
            pass

    time.sleep(1)
    try:
        if (("thankyou" in driver.current_url) or ("confirm" in driver.current_url)):
            log("лид отправлен")
            return True
        else:
            logBad("не удалось отправить лид")
            return False
    except UnexpectedAlertPresentException:
        logBad("не удалось отправить лид, UnexpectedAlertPresentException")
        return False

    time.sleep(1)

# проверка работы fbpixel на thankyou
def test_fbpixel_thankyou():
    if "fbq('track', 'PageView'" in driver.page_source:
        log("PageView на thankyou работает")
    else:
        logBad("PageView на thankyou не работает")
    if "fbq('track', 'Lead'" in driver.page_source:
        log("Lead на thankyou работает")
    else:
        logBad("Lead на thankyou не работает")

    if "fbq('init', '" in driver.page_source:
        if "fbq('init', '" + fbpixel in driver.page_source:
            log("на thankyou динамический fbpixel")
        else:
            logBad("на thankyou вшитый fbpixel")

# проверка наличия лида в лидроке
def test_lead_check():
    time.sleep(10)
    driver.get("https://leadrock.com/")
    cookies = pickle.load(open("cookies.pkl","rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get("https://leadrock.com/administrator/lead")
    time.sleep(3)
    try:
        driver.find_element_by_xpath("//td[contains(.,'" + str(lead) + "')]")
        log("лид дошел")
        return True
#        try:
#            driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[9]/a[contains(@class,'trash')]").click()
#            log("лид отправлен в trash")
#        except NoSuchElementException:
#            #driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[9]/a[contains(@class,'hold')]")
#            log("лид уже в trash")
    except NoSuchElementException:
        logBad("лид не дошел")
        return False


###################################################################
####################### ЗАПУСК ТЕСТИРОВАНИЯ #######################
###################################################################
try:
    with open("landings.txt", "r", encoding="utf-8") as f:
        lands = [row.strip() for row in f]
except OSError:
    print("landings.txt не найден")

log_add()

for land in lands:

    link = land + "?track_url=" + track_url + "&fbpixel=" + fbpixel
    lead = random.randint(1000000000, 9999999999)
    options = Options()
    options.add_argument('log-level=2')
    options.add_argument('--headless')
    driver = webdriver.Chrome(driver_path, options=options)

    log(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
    log(land)
    

    land_open()
    if test_available():
        test_global_lang()
#        test_elements_lang()
#        test_shipping_post()
        test_title()
        test_meta_lang("description")
        test_meta_lang("keywords")
        test_contacts()
        if test_policy_link():
            test_policy_blank()
            test_policy_available()
            test_policy_lang()
        if test_thankyou():
            time.sleep(1)
#            test_shipping_post()
        land_open()
        test_post_forms()
        test_get_forms()
        test_submit()
        test_required("name")
        test_required("phone")
        test_fbpixel_main()
        test_callback()
        if test_lead():
            test_fbpixel_thankyou()
#            test_lead_check()
    
    del globals()['lang']
    log("")
    driver.quit()


# .//tr[td[contains(.,'11111')]]/td[9]/a[contains(@class,'hold')]
# .//tr[td[contains(.,'eduard_testing@leadrock.com')]]/td[4]