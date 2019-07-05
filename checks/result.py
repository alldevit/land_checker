# Подведение итогов проверки ленда
def result(self):
    self.log("--------------------------------------")
    if len(self.log_bad_list) > 0:
        self.log("Замечаний: %s" % len(self.log_bad_list), force=True)
        for s in self.log_bad_list:
            self.log(s)
    else:
        self.log("Замечаний нет, %s идеален (но это не точно)" % self.site_type, force=True)
    self.log('', force=True)