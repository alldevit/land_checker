from requests import head

def page_exist(self):
    try:
        response = str(head(self.link))
        if '500' in response:
            self.logBad('ленд недоступен - 500')
            return False
        elif '403' in response:
            self.logBad('ленд недоступен - 403')
        elif 'No input file specified' in self.driver.page_source:
            self.logBad('ленд недоступен')
            return False
        else:
            return True
    except:
        return False