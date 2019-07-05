# Проверка наличия name и phone
# Считаем все формы, ищем поля с name - name и phone, сравниваем количество
def inputs_exist(self):
    inputs = ['name', 'phone']
    for elem in inputs:
        elem_num = len(self.f_xps("//input[@name='%s']" % elem))
        if self.form_num - elem_num > 0:
            self.logBad('пропущено поле %s' % elem)
            err = 1
    if 'err' not in locals():
        self.log('все необходимые поля на месте')