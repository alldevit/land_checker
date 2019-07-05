# Проверка языка конфирма
# Детектим язык текста на странице
def lang_confirm(self):
    result = self.lang_detect(self.f_tag('body').text, 'lib')
    self.compare(self.lang, result, 'thankyou')