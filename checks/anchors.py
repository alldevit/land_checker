from collections import Counter

# Анализ якорей на ленде
def anchors(self):
    if self.anchors_num > 0:
        anchors = []
        for i in range(1, self.anchors_num + 1):
            anchor = self.f_xp("(//*[contains(@href, '#')])[%s]" % i).get_attribute('href')
            anchors.append(anchor)
        c = list(Counter(anchors).items())
        self.log('%s якорей на ленде:' % self.anchors_num)
        for i in c:
            self.log('  %s "%s"' % (i[1], str(i[0]).split('#', 1)[1]))