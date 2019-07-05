from selenium.common.exceptions import NoSuchElementException

# Проверка доступности политики
# Переходим на политику и ищем "No input file specified"
def policy_exist(self):
    self.page_open(self.f_xp("//a[contains(@href,'policy')]").get_attribute("href"))
    try:
        self.f_xp('//*[contains(text(), "No input file specified")]')
        self.logBad('файл policy недоступен')
    except NoSuchElementException:
        if "google" in self.f_tag("body").text and 'privacy' in self.f_tag("body").text:
            self.log('файл policy на месте')
        else:
            self.logBad('политика недоступна')