from selenium.common.exceptions import NoSuchElementException

# Проверка наличия линка на политику
# Ищем ссылку "policy"
def policy_link(self):
    try:
        self.f_xp("//a[contains(@href,'policy')]")
        self.log('ссылка на policy на месте')
        return True
    except NoSuchElementException:
        self.logBad('ссылка на policy отсутствует')
        return False