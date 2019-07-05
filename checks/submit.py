# Проверка наличия submit
# Считаем все формы, кнопки submit и сравниваем количество
def submit(self):
    if self.form_num <= self.submit_num:
        self.log('во всех формах есть кнопка submit')
        return True
    else:
        x = self.form_num - self.submit_num
        self.logBad('для %s кнопок в форме(ах) пропущен submit' % x)
        return False