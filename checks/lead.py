from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException, UnexpectedAlertPresentException
import time

# Проверка наличия колеса удачи
def wheel(self):
    if self.wheel_exist > 0:
        self.log('обнаружено колесо, крутим')
        try:
            self.f_xp(".//div[contains(@class, 'wheel')]/span[contains(@class, 'cursor-text')]").click()
            time.sleep(10)
            self.f_xp("//a[@class='pop-up-button'][contains(.,'Ok')]").click()
            self.log('жмем ОК')
            time.sleep(2)
        except:
            pass

# Проверка валидатора
# Ищем input с красной обводкой валидатора
def validator(self):
    try:
        self.f_xp("//input[contains(@style,'outline: rgba(244, 67, 54, 0.85)')]")
        self.log('валидатор работает')
    except NoSuchElementException:
        self.logBad('валидатор не работает')
    except UnexpectedAlertPresentException:
        print('алерт')

# Отправка лида
# Заполняем все обязательные поля, жмем submit, чекаем валидатор, дописываем телефон, снова жмем submit
def lead(self):

    def send():
        for i in range(1, self.submit_num + 1):
            try:
                self.f_xp("(//*[@type='submit'])[%s]" % i).click()
            except:
                pass

    def check(output):
        time.sleep(1)
        try:
            if (("thankyou" in self.driver.current_url) or \
                ("confirm" in self.driver.current_url) or \
                ("order.php" in self.driver.current_url)):
                if output == True:
                    self.log("лид отправлен")
                return True
            else:
                if output == True:
                    self.logBad("не удалось отправить лид (конфирм не открылся)")
                return False
        except UnexpectedAlertPresentException:
            if output == True:
                self.logBad("не удалось отправить лид, UnexpectedAlertPresentException")
            return "error"

    def input_1():
        for i in range(1, self.req_num + 1): # в xpath индекс начинается с 1, а не с 0
            try:
                self.f_xp("(//input[@required])[%s]" % i).send_keys("1")
            except:
                pass

    def input_name():
        for i in range(1, self.name_num + 1):
            try:
                self.f_xp("(//input[@name='name'])[%s]" % i).send_keys(u'\ue003' + "test")
            except:
                pass

    def input_phone_first():
        for i in range(1, self.phone_num + 1):
            try:
                self.f_xp("(//input[@name='phone'])[%s]" % i).send_keys(u'\ue003' + str(self.lead))
            except:
                pass
    def input_phone_second():
        for i in range(1, self.phone_num + 1):
            try:
                self.f_xp("(//input[@name='phone'])[%s]" % i).send_keys(str(self.lead))
            except:
                pass
    
    wheel(self)

    input_1()
    input_name()
    input_phone_first()
    send()
    validator(self)
    result = check(False)
    if result == True:
        return check(True)
    elif result == False:
        input_phone_second()
        send()
        return check(True)
    else:
        self.logBad("ДОПИЛИТЬ ПРОВЕРКУ НАШЕГО ВАЛИДАТОРА при подключенном стороннем валидаторе")
        return False