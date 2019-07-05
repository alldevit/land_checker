# Проверка наличия юрлица
# Ищем 'GERARDE'
def contacts(self):
    if 'GERARDE' in self.replacer(self.source) or 'GЕRАRDЕ' in self.source:
        self.log('юрлицо на месте')
        return True
    else:
        self.logBad('юрлицо не указано')
        return False