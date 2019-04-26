import sys, os, time, random, requests, logging, re, string
from datetime import datetime
from selenium import webdriver
from collections import Counter
from urllib.parse import unquote

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from langdetect import detect
from googletrans import Translator
from google.cloud import translate
import pickle

from checker_config import *

#############################################################################################
####################################### СИСТЕМНЫЕ f() #######################################
#############################################################################################
error_num = 0

# создание синонимов основных функций поиска элементов
def f_xps(s):
    return driver.find_elements_by_xpath(s)
def f_tags(s):
    return driver.find_elements_by_tag_name(s)
def f_xp(s):
    return driver.find_element_by_xpath(s)
def f_tag(s):
    return driver.find_element_by_tag_name(s)

# получаем список лендов
def get_lands():
    global lands
    try:
        with open("landings.txt", "r", encoding="utf-8") as f:
            rows = [row for row in f]
            lands = []
            for row in rows:
                row = row.replace('\n', '')
                if " " in row:
                    tmp_array = row.split(' ')
                else:
                    tmp_array = [row]
                    
                lands.append(tmp_array)

    except OSError:
        print("landings.txt не найден")

# логирование -
def logBad(text):
    global error_num
    error_num += 1
    text = '- ' + str(text) + '\n'
    print(text[:-1])
    with open(mini_log, "a", encoding="utf-8") as f:
        f.write(text)

# логирование +
def log(text):
    print("  " + str(text))
    with open(mini_log, "a", encoding="utf-8") as f:
        f.write("  " + str(text) + "\n")

# сравниваем первый и второй аргумент, если второй не "en"
def compare(page_lang, elem_lang, elem):
    if elem_lang != "en":
        if page_lang == elem_lang:
            log("язык %s (%s) совпадает с языком страницы (%s)" % (elem, elem_lang, lang))
        else:
            logBad("язык %s (%s) не совпадает с языком страницы (%s)" % (elem, elem_lang, lang))
    else:
        log("язык %s (%s) совпадает с языком страницы (%s)" % (elem, elem_lang, lang))

# заменяем кириллицу на латиницу, если язык ленда не кириллический
def replacer(s):
    global str, lang
    if lang not in "ru, bg":
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
def lang_detect(text, method):
    global lang
    if 'lang' not in globals():
        lang = detect_methods[method](cleaner(text))
        if lang not in "ru, bg":
            lang = detect_methods[method](cleaner(replacer(text)))
        return lang
    else:
        if lang not in "ru, bg":
            local_lang = detect_methods[method](cleaner(replacer(text)))
        else:
            local_lang = detect_methods[method](cleaner(text))
        return local_lang

def lang_translate(text, method):
    global lang
    if lang != "ru":
        if lang != "bg":
            translated = translate_methods[method](cleaner(replacer(text)))
        else:
            translated = translate_methods[method](cleaner(text))
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

# определение, ленд/преленд
# считаем количество ссылок на странице
def test_is_land():
    if ((len(f_xps("//input[@name='name']")) > 0 or (len(f_tags("form")) - len(f_xps("//form[contains(@class, 'search')]"))) > 0) or ((len(f_tags("iframe")) - len(f_xps("//iframe[contains(@name, '_ym_native')]"))) > 0)) and\
            ("isPrelanding: true" not in driver.page_source) and\
            (len(f_tags("a")) < 50):
        log("ленд")
        return True
    else:
        log("преленд")
        return False

# анализ ссылкок на преленде
def test_pre_links():
    links_num = len(f_tags("a"))
    links = []
    for i in range(1, links_num + 1):
        try:
            link = f_xp("(//a)[" + str(i) + "]").get_attribute('href')
            links.append(link)
        except:
            pass
    c = list(Counter(links).items())
    log(str(links_num) + " ссылок на преленде:")
    correct_links = 0
    for i in c:
        correct_links += i[1]
        log(str(i[1]) + ' "' + str(i[0]) + '"')
    if correct_links != links_num:
        logBad("не удалось определить %s ссылок" % str(links_num - correct_links))

# анализ якорей на ленде
def test_anchors():
    anchors_num = len(f_xps("//*[contains(@href, '#')]"))
    if anchors_num > 0:
        anchors = []
        for i in range(1, anchors_num + 1):
            anchor = f_xp("(//*[contains(@href, '#')])[" + str(i) + "]").get_attribute('href')
            anchors.append(anchor)
        c = list(Counter(anchors).items())
        log(str(anchors_num) + " якорей на ленде:")
        for i in c:
            log('  %s "%s"' % (i[1], str(i[0]).split('#', 1)[1]))



# определение языка страницы
# детектим язык текста на странице
def test_global_lang():
    lang = lang_detect(f_tag("body").text, "lib")
    log(lang + " - язык страницы")

# определение языка каждого элемента
# вытягиваем текст, детектим язык всех строк по отдельности и сравниваем с языком ленда
def test_elements_lang():
    source_text = f_tag("body").text
    with open(lang_log, "a", encoding="utf-8") as f:
        f.write("\n" + land + "\n")
    strings = source_text.split("\n")
    lang_error = 0
    for s in strings:
        st = cleaner(s)
        if len(st) > 20:
            lang_s = lang_detect(st[:1000], "lib")
            print('.',sep='', end='', flush=True) # loadingbar
            if (lang != lang_s) and (lang_s != "en"):
                lang_s = lang_detect(st[:500], "cloud")
                if (lang != lang_s) and (lang_s != "en"):
                    with open(lang_log, "a", encoding="utf-8") as f:
                        f.write(lang_s + " is not " + lang + " " + s + "\n")
                    lang_error += 1
    print("")
    if lang_error == 0:
        log("язык всех элементов соответствует языку страницы")
    else:
        logBad("возможное несовпадение языка %s элементов" % lang_error)
    
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
        title = f_tag("title")
        log("title существует")
        lang_title = lang_detect(title.get_attribute('innerHTML'), "cloud")
        compare(lang, lang_title, "title")
        return True
    except NoSuchElementException:
        logBad("title отсутствует")
        return False

# проверка языка description и keywords
# ищем элементы, вытягиваем текст и детектим язык
def test_meta_lang(name):
    try:
        elem = f_xp("//meta[@name='" + name + "']")
        if len(elem.get_attribute("content")) > 0:
            lang_elem = lang_detect(elem.get_attribute("content"), "cloud")
            compare(lang, lang_elem, name)
    except NoSuchElementException:
        pass

# проверка наличия юрлица
# ищем "GERARDE"
def test_contacts():
    if "GERARDE" in replacer(driver.page_source) or "GЕRАRDЕ" in driver.page_source:
        log("юрлицо на месте")
        return True
    else:
        logBad("юрлицо не указано")
        return False

# проверка наличия линка на политику
# ищем ссылку "policy"
def test_policy_link():
    try:
        f_xp("//a[contains(@href,'policy')]")
        log("ссылка на policy на месте")
        return True
    except NoSuchElementException:
        logBad("ссылка на policy отсутствует")
        return False

# проверка открытия политики в новой вкладке
# ищем ссылку "policy" с атрибутом _blank
def test_policy_blank():
    try:
        f_xp("//a[contains(@href,'policy') and @target='_blank']")
        log("policy открывается в новой вкладке")
        return True
    except NoSuchElementException:
        logBad("policy не открывается в новой вкладке")
        return False

# проверка доступности политики
# переходим на политику и ищем "No input file specified"
def test_policy_exist():
    driver.get(f_xp("//a[contains(@href,'policy')]").get_attribute("href"))
    try:
        f_xp('//*[contains(text(), "No input file specified")]')
        logBad("файл policy недоступен")
    except NoSuchElementException:
        log("файл policy на месте")

# проверка языка политики
# детектим язык текста на странице
def test_policy_lang():
    lang_policy = lang_detect(f_tag("body").text, "lib")
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
    'lt':('370'),
    'el':('30')}
    
    if lang != "en":
        form_num = len(f_tags("form"))
        source = driver.page_source
        matches = 0
        for code in phone_codes[lang]:
            matches += len(re.findall(r'\+[\s]?' + code, source))

        if matches == form_num:
            log("во всех формах есть телефон с подходящим кодом")
        elif matches < form_num:
            logBad("не во всех формах есть телефон с подходящим кодом (%s телефонов / %s форм)" % (matches, form_num))
        else:
            logBad("необходимо проверить код телефона в подсказке (%s телефонов / %s форм)" % (matches, form_num))
    else:
        logBad("необходимо проверить код телефона в подсказке")

# проверка языка конфирма
# детектим язык текста на странице
def test_thankyou_lang():
    lang_thankyou = lang_detect(f_tag("body").text, "lib")
    compare(lang, lang_thankyou, "thankyou")

# проверка упоминания почты в тексте
# переводим текст на русский и ищем в нем "почт"
def test_shipping_post():
    source_text = f_tag("body").text.lower()
    if lang == "ru":
        if "почт" in source_text:
            logBad("в тексте упоминается почта")
    else:
        source_text_ru = lang_translate(source_text, "cloud")
        if "почт" in source_text_ru:
            logBad("в тексте упоминается почта")
            with open(post_log, "a", encoding="utf-8") as f:
                f.write(source_text_ru)

# проверка форм на POST
# считаем все формы, формы с методом POST и сравниваем количество
def test_post_forms():
    post_num = len(f_xps("//form[@method='POST' or @method='post']"))
    form_num = len(f_tags("form"))
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
        f_xp("//form[@method='GET' or @method='get']")
        logBad("на странице есть формы, отправляемые через GET")
        return False
    except NoSuchElementException:
        return True

# проверка наличия submit
# считаем все формы, кнопки submit и сравниваем количество
def test_submit():
    form_num = len(f_tags("form"))
    submit_num = len(f_xps("//*[@type='submit']"))
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
    form_num = len(f_tags("form"))
    for elem in inputs:
        elem_num = len(f_xps("//input[@name='" + elem + "']"))
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
        elem_num = len(f_xps("//input[@name='" + elem + "']"))
        if elem_num > 0:
            elem_req_num = len(f_xps("//input[@name='" + elem + "' and @required]"))
            if elem_num > elem_req_num:
                s += " " + elem
                e = e + elem_num - elem_req_num

    if len(s) > 0:
        logBad("пропущен required для полей" + s)

# проверка не-required полей
# считаем все поля, все поля с required, поля notes и вычитаем из первых вторые, третие, и поля из предыдущего теста
def test_nonrequired_input():
    input_num = len(f_xps("(//input[@type='text'])"))
    input_req_num = len(f_xps("(//input[@type='text' and @required])"))
    notes_elems = ['other[note]', 'other[notes]', 'other[comment]']
    notes_num = 0
    for elem in notes_elems:
        try:
            notes_num += len(f_xps("//input[@name='" + elem + "']"))
        except:
            pass
    global e
    i = input_num - input_req_num - notes_num - e
    if i > 0:
        logBad(str(i) + " полей без required")

# проверка наличия коллбэка
# считаем количество полей в формах, ищем картинку коллбэка
def test_callback():
    form_num = len(f_tags("form"))
    input_num = len(f_tags("input"))
    if form_num == 0: form_num = 1
    if (input_num/form_num) < 3:
        if 'i-phone.png' in driver.page_source or'phone.png' in driver.page_source:
            log("коллбэк на месте")
            return True
        else:
            logBad("коллбэк отсутствует")
            return False
    else:
        log("коллбэк не требуется")
        return True

# проверка отсутствия поля e-mail
# ищем поле, содержащее в name "email"
def test_email():
    num_email = len(f_xps("//input[contains(@name, 'email')]"))
    if num_email > 0:
        logBad("в форме присутствует поле email")


# проверка валидатора
# ищем input с красной обводкой валидатора
def test_validator():
    try:
        f_xp("//input[contains(@style,'outline: rgba(244, 67, 54, 0.85)')]")
        log("валидатор работает")
    except NoSuchElementException:
        logBad("валидатор не работает")

# проверка наличия колеса удачи
def test_wheel():
    try:
        f_xp(".//div[contains(@class, 'wheel')]/span[contains(@class, 'cursor-text')]").click()
        print("  обнаружено колесо, крутим")
        time.sleep(10)
        f_xp("//a[@class='pop-up-button'][contains(.,'Ok')]").click()
        print("  жмем ОК")
        time.sleep(2)
    except:
        pass

# отправка лида
# заполняем все обязательные поля, жмем submit, чекаем валидатор, дописываем телефон, снова жмем submit
def test_lead():
    submit_num = len(f_xps("//*[@type='submit']"))
    req_num = len(f_xps("//input[@required]"))
    name_num = len(f_xps("//input[@name='name']"))
    phone_num = len(f_xps("//input[@name='phone']"))

    def send():
        for i in range(1, submit_num + 1):
            try:
                f_xp("(//*[@type='submit'])[" + str(i) + "]").click()
            except:
                pass

    def check(output):
        time.sleep(1)
        try:
            if (("thankyou" in driver.current_url) or \
                ("confirm" in driver.current_url) or \
                ("order.php" in driver.current_url)):
                if output == True: log("лид отправлен")
                return True
            else:
                if output == True: logBad("не удалось отправить лид (конфирм не открылся)")
                return False
        except UnexpectedAlertPresentException:
            if output == True: logBad("не удалось отправить лид, UnexpectedAlertPresentException")
            return "error"

    def input_1():
        for i in range(1, req_num + 1): # в xpath индекс начинается с 1, а не с 0
            try:
                f_xp("(//input[@required])[" + str(i) + "]").send_keys("1")
            except:
                pass

    def input_name():
        for i in range(1, name_num + 1):
            try:
                f_xp("(//input[@name='name'])[" + str(i) + "]").send_keys(u'\ue003' + "test")
            except:
                pass

    def input_phone_1():
        for i in range(1, phone_num + 1):
            try:
                f_xp("(//input[@name='phone'])[" + str(i) + "]").send_keys(u'\ue003' + str(lead))
            except:
                pass
    def input_phone_2():
        for i in range(1, phone_num + 1):
            try:
                f_xp("(//input[@name='phone'])[" + str(i) + "]").send_keys(str(lead))
            except:
                pass
    
    test_wheel()

    input_1()
    input_name()
    input_phone_1()
    send()
    test_validator()
    result = check(False)
    if result == True:
        return check(True)
    elif result == False:
        input_phone_2()
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
            logBad("на %s вшитый fbpixel - %s" % (page, real_pixel))

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
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(.,'" + str(lead) + "') and contains(.,'test')]")))
        log("лид дошел")
        try:
            f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[4]/i[contains(@class,'fa-spinner')]")
            f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[10]/a[contains(@class,'trash')]").click()
            time.sleep(1)
            f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[4]/i[contains(@class,'fa-trash-o')]")
            log("лид отправлен в trash")
        except NoSuchElementException:
            #f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[9]/a[contains(@class,'hold')]")
            try:
                f_xp(".//tr[td[contains(.,'" + str(lead) + "')]]/td[4]/i[contains(@class,'fa-trash-o')]")
                log("лид уже в trash")
            except:
                logBad("не удалось отправить в trash лид c телефоном " + str(lead))
    except:
        logBad("не удалось найти лид c телефоном " + str(lead))
        return False

def test_result():
    global error_num
    if error_num > 0:
        log("--------------------------------------")
        log("Выявлено %s возможных ошибок" % error_num)
    else:
        log("--------------------------------------")
        log("Ошибок не выявлено")

#############################################################################################
####################################### ЗАПУСК ТЕСТОВ #######################################
#############################################################################################

log_add()
get_lands()

for row in lands:

    error_num = 0

    options = Options()
    options.add_argument('log-level=2')
    options.add_argument('--headless') # закомментировать для отключения headless-режима
    options.add_argument('--incognito')
#    options.add_argument('--disable-images')
    driver = webdriver.Chrome(driver_path, options=options)
    driver.delete_all_cookies()
    log(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))

    land = row[0]
    if len(row) > 1:
        if "URL" in row[1]:
            track_url = row[1]
            log(row[0] + " " + row[1])
        else:
            track_url = default_track_url
            log(row[0])
    else:
        track_url = default_track_url
        log(row[0])

    link = land + "?track_url=" + track_url + "&fbpixel=" + fbpixel
    lead = random.randint(1000, 9999)

    

    land_open()
    if test_land_exist():
        if test_is_land():
            
# запуск тестов для ленда
            test_global_lang()
            test_elements_lang()
#            test_shipping_post()
            test_title()
            test_meta_lang("description")
            test_meta_lang("keywords")
            test_contacts()
            if test_policy_link():
                test_policy_blank()
                test_policy_exist()
                test_policy_lang()
            land_open()
            test_callback()
            test_anchors()
            test_phone_code()
            test_post_forms()
            test_get_forms()
            test_submit()
            test_input_exist()
            test_required_input()
            test_nonrequired_input()
            test_email()
            test_fbpixel("ленде")
            if test_lead():
                test_fbpixel("thankyou")
                test_thankyou_lang()
                test_shipping_post()
                test_lead_check()

# запуск тестов для преленда
        else:
            test_global_lang()
            test_elements_lang()
            test_title()
            test_meta_lang("description")
            test_meta_lang("keywords")
            test_pre_links()
    test_result()
    try:
        del globals()['lang']
    except:
        pass
    log("")
    driver.quit()


# .//tr[td[contains(.,'11111')]]/td[9]/a[contains(@class,'hold')]
# .//tr[td[contains(.,'eduard_testing@leadrock.com')]]/td[4]