# Проверка упоминания почты в тексте
# Переводим текст на русский и ищем в нем "почт"
def shipping_post(self):
    source_text = self.f_tag('body').text.lower()
    if self.lang == 'ru':
        if 'почт' in source_text:
            self.logBad('на thankyou упоминается почта')
    else:
        source_text_ru = self.lang_translate(source_text, 'cloud')
        if 'почт' in source_text_ru:
            self.logBad('на thankyou упоминается почта')