def forms_action(self):
    if self.form_num != self.action_num:
        self.logBad('в %s формах пропущен action' % (self.form_num - self.action_num))
    else:
        self.log('для всех форм установлен action')