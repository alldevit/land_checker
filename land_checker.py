# Установка базовых модулей:
# python -m pip install --upgrade pip
# pip install selenium langdetect googletrans google-cloud-translate requests 
# 

import sys, os, time, random, requests, logging, re, string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from urllib.parse import unquote

from langdetect import detect
from googletrans import Translator
from google.cloud import translate
import pickle

from checker_config import *


#############################################################################################
####################################### СИСТЕМНЫЕ f() #######################################
#############################################################################################

# получаем список лендов
def get_lands():
    global lands
    try:
        with open("landings.txt", "r", encoding="utf-8") as f:
            rows = [row for row in f]
            lands = []
            for row in rows:
                if " " in row:
                    tmp_array = row.split(' ')
                else:
                    tmp_array = [row]
                    
                lands.append(tmp_array)

    except OSError:
        print("landings.txt не найден")

def logBad(text):
    text = '- ' + str(text) + '\n'
    print(text[:-1])
    with open(mini_log, "a", encoding="utf-8") as f:
        f.write(text)

def log(text):
    print("  " + str(text))
    with open(mini_log, "a", encoding="utf-8") as f:
        f.write("  " + str(text) + "\n")

# сравниваем первый и второй аргумент, если второй не "en"
def compare(page_lang, elem_lang, elem):
    if elem_lang != "en":
        if page_lang == elem_lang:
            log("язык " + elem + " совпадает с языком страницы " + elem_lang)
        else:
            logBad("язык " + elem + " не совпадает с языком страницы " + elem_lang)
    else:
        log("язык " + elem + " совпадает с языком страницы " + elem_lang)

# заменяем кириллицу на латиницу, если язык ленда не кириллический
def replacer(s):
    global str, lang
    if lang != "ru" and lang != "bg":
        trans_table = str.maketrans("аеосрхАЕОСРХ","aeocpxAEOCPX")
        return s.translate(trans_table)
    else:
        return s

# открываем ленд и ждем секунду
def land_open():
    driver.get(link)
    time.sleep(1)

# переносим содержимое последнего лога в полный лог и удаляем файл
def log_add():
    try:
        with open(mini_log, "r", encoding="utf-8") as f:
            txt = f.read()
        with open(full_log, "a", encoding="utf-8") as f:
            f.write(txt)
        os.remove(mini_log)
    except OSError:
        pass

# удаляем повторяющиеся пробелы и все цифры 
def cleaner(s):
    return re.sub(r'\s+', ' ', re.sub(r"\d+", "", s))

#############################################################################################
###################################### РАБОТА С ЯЗЫКОМ ######################################
#############################################################################################
def lang_detect(text):
    global lang
    if 'lang' not in globals():
        lang = detect_methods[translate_method](cleaner(text))
        if lang != "ru" and lang != "bg":
            lang = detect_methods[translate_method](cleaner(replacer(text)))
        return lang
    else:
        if lang != "ru" and lang != "bg":
            local_lang = detect_methods[translate_method](cleaner(replacer(text)))
        else:
            local_lang = detect_methods[translate_method](cleaner(text))
        return local_lang

def lang_translate(text):
    global lang
    if lang != "ru":
        if lang != "bg":
            translated = translate_methods[translate_method](cleaner(replacer(text)))
        else:
            translated = translate_methods[translate_method](cleaner(text))
    else:
        translated = text
    return translated

def detect_lib(s):
    return detect(s)

def translate_lib(s):
    return s

def detect_cloud(s):
    client = translate.Client()
    detected = client.detect_language(s)
    return detected["language"]

def translate_cloud(s):
    translate_client = translate.Client()
    translated = translate_client.translate(s, "ru")
    return translated["translatedText"]

def detect_api(s):
    time.sleep(0.5)
    translator = Translator()
    detected = translator.detect(s[:5000])
    return getattr(detected, "lang")[:2]

def translate_api(s):
    text_array = [s[i:i+4500] for i in range(0,len(s),4500)]
    translated = ""
    for s in text_array:
        time.sleep(0.5)
        translator = Translator()
        g_query = translator.translate((s), dest="ru")
        translated = translated + getattr(g_query, "text")
    return translated

translate_methods = {'lib':translate_lib, 'cloud':translate_cloud, 'api':translate_api}
detect_methods = {'lib':detect_lib, 'cloud':detect_cloud, 'api':detect_api}


#############################################################################################
########################################### ТЕСТЫ ###########################################
#############################################################################################
# определение языка ленда
# детектим язык текста на странице
def test_global_lang():
    lang = lang_detect(driver.find_element_by_tag_name("body").text)
    log(lang + " - язык ленда")

# определение языка каждого элемента
# вытягиваем текст, детектим язык всех строк по отдельности и сравниваем с языком ленда
def test_elements_lang():
    source_text = driver.find_element_by_tag_name("body").text
    with open(lang_log, "a", encoding="utf-8") as f:
        f.write("\n" + land + "\n")
    strings = source_text.split("\n")
    lang_error = 0
    for s in strings:
        st = cleaner(s)
        if len(st) > 20:
            lang_s = lang_detect(st[:1000])
            print('.',sep='', end='', flush=True) # loadingbar
            if (lang != lang_s) and (lang_s != "en"):
                global translate_method
                if translate_method == "lib":
                    tmp = translate_method
                    translate_method = "cloud" # ! ! !
                    lang_s = lang_detect(st[:500])
                    if (lang != lang_s) and (lang_s != "en"):
                        with open(lang_log, "a", encoding="utf-8") as f:
                            f.write(lang_s + " is not " + lang + " " + s + "\n")
                        lang_error += 1
                    translate_method = tmp
                else:
                    with open(lang_log, "a", encoding="utf-8") as f:
                        f.write(lang_s + " is not " + lang + " " + s + "\n")
                    lang_error += 1
    print("")
    if lang_error > 0:
        logBad("возможное несовпадение языка " + str(lang_error) + " элементов")
    
# проверка доступности ленда
# ищем "500" или "No input file specified"
def test_land_exist():
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
# ищем <title> и детектим язык содержимого
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
# ищем элементы, вытягиваем текст и детектим язык
def test_meta_lang(name):
    try:
        elem = driver.find_element_by_xpath("//meta[@name='" + name + "']")
        if len(elem.get_attribute("content")) > 0:
            lang_elem = lang_detect(elem.get_attribute("content"))
            compare(lang, lang_elem, name)
    except NoSuchElementException:
        pass

# проверка наличия юрлица
# ищем "GERARDE"
def test_contacts():
    if "GERARDE" in replacer(driver.page_source):
        log("юрлицо на месте")
        return True
    else:
        logBad("юрлицо не указано")
        return False

# проверка наличия линка на политику
# ищем ссылку "policy"
def test_policy_link():
    try:
        driver.find_element_by_xpath("//a[contains(@href,'policy')]")
        log("ссылка на policy на месте")
        return True
    except NoSuchElementException:
        logBad("ссылка на policy отсутствует")
        return False

# проверка открытия политики в новой вкладке
# ищем ссылку "policy" с атрибутом _blank
def test_policy_blank():
    try:
        driver.find_element_by_xpath("//a[contains(@href,'policy') and @target='_blank']")
        log("policy открывается в новой вкладке")
        return True
    except NoSuchElementException:
        logBad("policy не открывается в новой вкладке")
        return False

# проверка доступности политики
# переходим на политику и ищем "No input file specified"
def test_policy_exist():
    driver.get(driver.find_element_by_xpath("//a[contains(@href,'policy')]").get_attribute("href"))
    try:
        driver.find_element_by_xpath('//*[contains(text(), "No input file specified")]')
        logBad("файл policy недоступен")
    except NoSuchElementException:
        log("файл policy на месте")

# проверка языка политики
# детектим язык текста на странице
def test_policy_lang():
    lang_policy = lang_detect(driver.find_element_by_tag_name("body").text)
    compare(lang, lang_policy, "policy")

# проверка соответствия кода телефона стране
# ищем упоминания кода телефона, сравниваем с количеством форм на странице
def test_phone_code():
    phone_codes = {'mk':('389'),
    'sq':('389'),
    'cs':('420'),
    'zh':('852', '886'),
    'et':('372'),
    'ar':('966', '965', '973', '971', '968', '221', '212'),
    'uk':('380'),
    'sw':('255', '254', '256'),
    'sl':('386'),
    'de':('43', '49', '32', '41'),
    'fl':('63'),
    'pl':('48'),
    'es':('591', '593', '51', '54', '34', '52', '57'),
    'id':('62'),
    'th':('66'),
    'ru':('7'),
    'hi':('91'),
    'it':('39', '41'),
    'sk':('421'),
    'hu':('36'),
    'nl':('32', '31'),
    'ms':('60'),
    'fi':('358'),
    'sv':('358'),
    'vi':('84'),
    'bs':('387'),
    'sr':('387', '381'),
    'hr':('387', '385'),
    'fr':('32', '41', '33', '221'),
    'pt':('55', '351'),
    'bg':('359'),
    'ro':('40'),
    'si':('94'),
    'ta':('94'),
    'lv':('371'),
    'lt':('370')}
    
    if lang != "en":
        form_num = len(driver.find_elements_by_tag_name("form"))
        source = driver.page_source
        matches = 0
        for code in phone_codes[lang]:
            matches += len(re.findall(r'\+[\s]?' + code, source))

        if matches == form_num:
            log("во всех формах есть телефон с подходящим кодом")
        elif matches < form_num:
            logBad("не во всех формах есть телефон с подходящим кодом (" + str(matches) + " телефонов / " + str(form_num) + " форм)")
        else:
            logBad("баг поиска телефона в ленде")
    else:
        logBad("необходимо проверить код телефона в подсказке")

# проверка языка конфирма
# детектим язык текста на странице
def test_thankyou_lang():
    lang_thankyou = lang_detect(driver.find_element_by_tag_name("body").text)
    compare(lang, lang_thankyou, "thankyou")

# проверка упоминания почты в тексте
# переводим текст на русский и ищем в нем "почт"
def test_shipping_post():
    source_text = driver.find_element_by_tag_name("body").text.lower()
    if lang == "ru":
        if "почт" in source_text:
            logBad("в тексте упоминается почта")
    else:
        source_text_ru = lang_translate(source_text)
        if "почт" in source_text_ru:
            logBad("в тексте упоминается почта")
            with open(post_log, "a", encoding="utf-8") as f:
                f.write(source_text_ru)

# проверка форм на POST
# считаем все формы, формы с методом POST и сравниваем количество
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
# ищем формы с методом GET
def test_get_forms():
    try:
        driver.find_element_by_xpath("//form[@method='GET' or @method='get']")
        logBad("на странице есть формы, отправляемые через GET")
        return False
    except NoSuchElementException:
        return True

# проверка наличия submit
# считаем все формы, кнопки submit и сравниваем количество
def test_submit():
    form_num = len(driver.find_elements_by_tag_name("form"))
    submit_num = len(driver.find_elements_by_xpath("//*[@type='submit']"))
    if form_num == submit_num:
        log("во всех формах есть кнопка submit")
        return True
    else:
        x = form_num - submit_num
        logBad("для " + str(x) + " кнопок в форме(ах) пропущен submit")
        return False

# проверка наличия name и phone
# считаем все формы, ищем поля с name - name и phone, сравниваем количество
def test_input_exist():
    err = 0
    inputs = ['name', 'phone']
    form_num = len(driver.find_elements_by_tag_name("form"))
    for elem in inputs:
        elem_num = len(driver.find_elements_by_xpath("//input[@name='" + elem + "']"))
        if form_num - elem_num > 0:
            logBad("пропущено поле " + elem)
            err = 1
    if err == 0:
        log("все необходимые поля на месте")

# проверка required для полей
# считаем поля, считаем такие же поля с required, сравниваем количество
def test_required_input():
    global e
    e = 0
    s = ""
    field_names = ['name', 'phone', 'other[address]', 'other[city]', 'other[zipcode]', 'other[quantity]']
    for elem in field_names:
        elem_num = len(driver.find_elements_by_xpath("//input[@name='" + elem + "']"))
        if elem_num > 0:
            elem_req_num = len(driver.find_elements_by_xpath("//input[@name='" + elem + "' and @required]"))
            if elem_num > elem_req_num:
                s += " " + elem
                e = e + elem_num - elem_req_num

    if len(s) > 0:
        logBad("пропущены required для полей" + s)

# проверка не-required полей
# считаем все поля, все поля с required, поля notes и вычитаем из первых вторые, третие, и поля из предыдущего теста
def test_nonrequired_input():
    input_num = len(driver.find_elements_by_xpath("(//input[@type='text'])"))
    input_req_num = len(driver.find_elements_by_xpath("(//input[@type='text' and @required])"))
    notes_elems = ['other[note]', 'other[notes]']
    notes_num = 0
    for elem in notes_elems:
        try:
            notes_num += len(driver.find_elements_by_xpath("//input[@name='" + elem + "']"))
        except:
            pass
    global e
    i = input_num - input_req_num - notes_num - e
    if i > 0:
        logBad(str(i) + " полей без required")

# проверка наличия коллбэка
# считаем количество полей в формах, ищем картинку коллбэка
def test_callback():
    form_num = len(driver.find_elements_by_tag_name("form"))
    input_num = len(driver.find_elements_by_tag_name("input"))
    if form_num == 0: form_num = 1
    if (input_num/form_num) < 3:
        if 'img/i-phone.png' in driver.page_source or 'img/phone.png' in driver.page_source:
            log("коллбэк на месте")
            return True
        else:
            logBad("коллбэк отсутствует")
            return False
    else:
        log("коллбэк не требуется")
        return True

# проверка валидатора
# ищем input с красной обводкой валидатора
def test_validator():
    try:
        driver.find_element_by_xpath("//input[contains(@style,'outline: rgba(244, 67, 54, 0.85)')]")
        log("валидатор работает")
    except NoSuchElementException:
        logBad("валидатор не работает")

# проверка наличия колеса удачи
def test_wheel():
    try:
        driver.find_element_by_xpath(".//div[contains(@class, 'wheel')]/span[contains(@class, 'cursor-text')]").click()
        print("  обнаружено колесо, крутим")
        time.sleep(10)
        driver.find_element_by_xpath("//a[@class='pop-up-button'][contains(.,'Ok')]").click()
        time.sleep(1)
    except:
        pass

# отправка лида
# заполняем все обязательные поля, жмем submit, чекаем валидатор, дописываем телефон, снова жмем submit
def test_lead():
    submit_num = len(driver.find_elements_by_xpath("//*[@type='submit']"))
    req_num = len(driver.find_elements_by_xpath("//input[@required]"))
    name_num = len(driver.find_elements_by_xpath("//input[@name='name']"))
    phone_num = len(driver.find_elements_by_xpath("//input[@name='phone']"))

    def send():
        for i in range(1, submit_num + 1):
            try:
                driver.find_element_by_xpath("(//*[@type='submit'])[" + str(i) + "]").click()
            except:
                pass

    def check(output):
        time.sleep(1)
        try:
            if (("thankyou" in driver.current_url) or ("confirm" in driver.current_url)):
                if output == True: log("лид отправлен")
                return True
            else:
                if output == True: logBad("не удалось отправить лид")
                return False
        except UnexpectedAlertPresentException:
            if output == True: logBad("не удалось отправить лид, UnexpectedAlertPresentException")
            return "error"

    def input_1():
        for i in range(1, req_num + 1): # в xpath индекс начинается с 1, а не с 0
            try:
                driver.find_element_by_xpath("(//input[@required])[" + str(i) + "]").send_keys("1")
            except:
                pass

    def input_name():
        for i in range(1, name_num + 1):
            try:
                driver.find_element_by_xpath("(//input[@name='name'])[" + str(i) + "]").send_keys("test")
            except:
                pass

    def input_phone():
        for i in range(1, phone_num + 1):
            try:
                driver.find_element_by_xpath("(//input[@name='phone'])[" + str(i) + "]").send_keys(lead)
            except:
                pass
    
    test_wheel()

    input_1()
    input_name()
    send()
    test_validator()
    result = check(False)
    if result == True:
        return check(True)
    elif result == False:
        input_phone()
        send()
        return check(True)
    else:
        logBad("ДОПИЛИТЬ ПРОВЕРКУ НАШЕГО ВАЛИДАТОРА при подключенном стороннем валидаторе")
        return False


# проверка работы fbpixel
# ищем код событий пикселя, ищем код пикселя из конфига
def test_fbpixel(page):
    if "fbq('track', 'PageView'" in driver.page_source:
        log("PageView на " + page + " работает")
    else:
        logBad("PageView на " + page + " не работает")
    
    if page == "thankyou":
        if "fbq('track', 'Lead'" in driver.page_source:
            log("Lead на " + page + " работает")
        else:
            logBad("Lead на " + page + " не работает")
    
    a = driver.page_source.split("\n")
    for s in a:
        if "fbq('init', '" in s:
            real_pixel = re.sub("\D", "", s)

    if "fbq('init', '" in driver.page_source:
        if "fbq('init', '" + fbpixel in driver.page_source:
            log("на " + page + " динамический fbpixel")
        else:
            logBad("на " + page + " вшитый fbpixel - " + str(real_pixel))

# проверка наличия лида в лидроке
# открываем лидрок, грузим куки, ищем lead
def test_lead_check():
    time.sleep(1)
    driver.get("https://leadrock.com/")
    cookies = pickle.load(open("cookies.pkl","rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get("https://leadrock.com/administrator/lead")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(.,'" + str(lead) + "')]")))
        log("лид дошел")
        try:
            driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[4]/i[contains(@class,'fa-spinner')]")
            driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[10]/a[contains(@class,'trash')]").click()
            time.sleep(0.5)
            driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[4]/i[contains(@class,'fa-trash-o')]")
            log("лид отправлен в trash")
        except NoSuchElementException:
            #driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[9]/a[contains(@class,'hold')]")
            try:
                driver.find_element_by_xpath(".//tr[td[contains(.,'" + str(lead) + "')]]/td[4]/i[contains(@class,'fa-trash-o')]")
                log("лид уже в trash")
            except:
                logBad("проверить статус лида c телефоном 1" + str(lead))
    except:
        logBad("проверить статус лида c телефоном 1" + str(lead))
        return False


#############################################################################################
####################################### ЗАПУСК ТЕСТОВ #######################################
#############################################################################################

get_lands()
log_add()

for row in lands:

    land = row[0]
    if len(row) > 1:
        if "URL" in row[1]:
            track_url = row[1]
        else:
            track_url = default_track_url
    else:
        track_url = default_track_url

    link = land + "?track_url=" + track_url + "&fbpixel=" + fbpixel
    lead = random.randint(1000000000, 9999999999)
    options = Options()
    options.add_argument('log-level=2')
    options.add_argument('--headless')
    driver = webdriver.Chrome(driver_path, options=options)

    log(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
    log(land)
    

    land_open()
    if test_land_exist():
        test_global_lang()
        test_elements_lang()
        test_shipping_post()
        test_title()
        test_meta_lang("description")
        test_meta_lang("keywords")
        test_contacts()
        if test_policy_link():
            test_policy_blank()
            test_policy_exist()
            test_policy_lang()
        land_open()
        test_phone_code()
        test_post_forms()
        test_get_forms()
        test_submit()
        test_input_exist()
        test_required_input()
        test_nonrequired_input()
        test_fbpixel("ленде")
        test_callback()
        if test_lead():
            test_fbpixel("thankyou")
            test_thankyou_lang()
            test_shipping_post()
            test_lead_check()

    del globals()['lang']
    log("")
    driver.quit()


# .//tr[td[contains(.,'11111')]]/td[9]/a[contains(@class,'hold')]
# .//tr[td[contains(.,'eduard_testing@leadrock.com')]]/td[4]