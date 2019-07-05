from selenium.common.exceptions import NoSuchElementException

# Проверка языка description и keywords
# Ищем элементы, вытягиваем текст и детектим язык
def lang_meta(self):
    elems = ['keywords', 'description']
    for name in elems:
        try:
            elem = self.f_xp("//meta[@name='%s']" % name)
            if len(elem.get_attribute('content')) > 1:
                lang_elem = self.lang_detect(elem.get_attribute('content'), 'cloud')
                self.compare(self.lang, lang_elem, name)
        except NoSuchElementException:
            pass