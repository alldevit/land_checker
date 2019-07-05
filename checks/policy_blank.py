from selenium.common.exceptions import NoSuchElementException


# Проверка открытия политики в новой вкладке
# Ищем ссылку "policy" с атрибутом _blank
def policy_blank(self):
    try:
        self.f_xp("//a[contains(@href,'policy') and @target='_blank']")
        self.log('policy открывается в новой вкладке')
        return True
    except NoSuchElementException:
        self.logBad('policy не открывается в новой вкладке')
        return False