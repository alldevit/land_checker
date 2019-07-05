# Проверка языка политики
# Детектим язык текста на странице
def policy_lang(self):
    lang_policy = self.lang_detect(self.f_tag('body').text, 'lib')
    self.compare(self.lang, lang_policy, 'policy')