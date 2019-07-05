# Определение языка каждого элемента
# Вытягиваем текст, детектим язык всех строк по отдельности и сравниваем с языком ленда
def lang_elements(self):
    with open(self.LOG_LANG, 'a', encoding='utf-8') as f:
        try:
            f.write('\n' + self.land + '\n')
        except:
            pass
    strings = self.page_text.split('\n')
    lang_error = 0
    for s in strings:
        st = self.cleaner(s)
        if len(st) > 20:
            lang_s = self.lang_detect(st[:1000], 'lib')
            print('.',sep='', end='', flush=True) # loadingbar
            if (self.lang != lang_s) and (lang_s != 'en'):
                lang_s = self.lang_detect(st[:500], 'cloud')
                if (self.lang != lang_s) and (lang_s != 'en'):
                    with open(self.LOG_LANG, 'a', encoding='utf-8') as f:
                        f.write(lang_s + ' is not ' + self.lang + ' ' + s + '\n')
                    lang_error += 1
    print('')
    if lang_error == 0:
        self.log('язык всех элементов соответствует языку страницы')
    else:
        self.logBad('возможное несовпадение языка %s элементов' % lang_error)