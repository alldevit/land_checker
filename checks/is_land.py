def is_land(self):
#    return False
#    return True
    if (((self.name_num > 0 or (self.form_num - self.search_num) > 0) or (self.iframe_num > 0)) and
            ('isPrelanding: true' not in self.source) and
            (len(self.f_tags('a')) < 75) and
            ('/pre/' not in self.land)):
        self.site_type = 'ленд'
        self.log(self.site_type)
        return True
    else:
        self.site_type = 'преленд'
        self.log(self.site_type)
        return False

# and ('https://leadrock.com/URL-' not in self.source)