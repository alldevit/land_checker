# Проверка наличия GET форм
# Ищем формы с методом GET
def forms_get(self):
    if self.get_num > 0:
        self.logBad('на странице есть формы, отправляемые через GET')
        return False
    else:
        return True