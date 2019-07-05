# Проверка наличия коллбэка
# Считаем количество полей в формах, ищем картинку коллбэка
def callback(self):
    if '/TOV-' not in self.driver.current_url:
        try:
            if (self.input_num / self.form_num) < 3:
                if 'i-phone.png' in self.source or'phone.png' in self.source:
                    self.log('коллбэк на месте')
                    return True
                else:
                    self.logBad('коллбэк отсутствует')
                    return False
            else:
                self.log('коллбэк не требуется')
                return True
        except:
            self.logBad('на странице нет форм, коллбэк не определен')