# Определение языка страницы
# Детектим язык видимого текста на странице
def lang_main(self):
    self.lang = self.lang_detect_page(self.f_tag('body').text)
    self.log('%s - основной язык' % self.lang)
    return self.lang