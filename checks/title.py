def title(self):
    try:
        title = self.f_tag('title')
        title_text = title.get_attribute('innerHTML')
        if ' ' in title_text:
            title_lang = self.lang_detect(title_text, 'cloud')
            self.compare(self.lang, title_lang, 'title')
        else:
            self.log('title слишком короткий для проверки языка')
    except:
        self.logBad('title не нейден')