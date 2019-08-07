from collections import Counter

# Анализ ссылкок на преленде
def pre_links(self):
    links = []
    for i in range(1, self.links_num + 1):
        try:
            link = self.f_xp("(//a)[%s]" % i).get_attribute('href')
            links.append(link)
        except:
            pass
    c = list(Counter(links).items())
    self.log('%s ссылок на преленде:' % self.links_num, force=True)
    correct_links = 0
    for i in c:
        correct_links += i[1]
        self.log('%s "%s"' % (i[1], i[0]), force=True)
    if correct_links != self.links_num:
        self.logBad('не удалось определить %s ссылок' % self.links_num - correct_links)
    
    if self.links_num != (c[0])[1]:
        self.logBad('не все ссылки на преленде одинаковы')
