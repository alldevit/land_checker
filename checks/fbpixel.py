import re

# проверка работы fbpixel
# ищем код событий пикселя, ищем код пикселя из конфига
def fbpixel(self, page):
    if "fbq('track', 'PageView'" in self.driver.page_source:
        self.log('PageView на %s работает' % page)
    else:
        self.logBad('PageView на %s не работает' % page)
    
    if page == 'thankyou':
        if "fbq('track', 'Lead'" in self.driver.page_source:
            self.log('Lead на %s работает' % page)
        else:
            self.logBad('Lead на %s не работает' % page)
    
    a = self.driver.page_source.split('\n')
    for s in a:
        if "fbq('init', '" in s:
            real_pixel_script = re.sub('\D', '', s)
        if "www.facebook.com/tr?id=" in s:
            real_pixel_img = s.split('www.facebook.com/tr?id=')[1].split('&')[0]

    if "fbq('init', '" in self.driver.page_source:
        if "fbq('init', '" + self.FBPIXEL in self.driver.page_source:
            self.log('на %s динамический fbpixel' % page)
        else:
            self.logBad('на %s вшитый fbpixel - %s' % (page, real_pixel_script))

    # try:
    #     self.logBad('на %s вшитый fbpixel - %s' % (page, real_pixel_img))
    # except:
    #     pass