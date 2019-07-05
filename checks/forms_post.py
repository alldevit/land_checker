# Проверка форм на POST
# Считаем все формы, формы с методом POST и сравниваем количество
def forms_post(self):
    if self.form_num == self.post_num:
        self.log('все формы отправляются через POST')
        return True
    else:
        self.logBad('%s форм из %s отправляется не через POST' % (self.form_num - self.post_num, self.form_num))
        return False