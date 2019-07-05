# Проверка отсутствия поля e-mail
# Ищем поле, содержащее в name "email"
def input_email(self):
    if self.email_num > 0:
        self.logBad('в форме присутствует поле email')