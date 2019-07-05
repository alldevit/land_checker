# Проверка не-required полей
# Считаем все поля, все поля с required, поля notes и вычитаем из первых вторые, третие, и поля из предыдущего теста
def inputs_nonrequired(self):        
    notes_elems = ['other[notes]', 'other[comment]']
    notes_num = 0
    for elem in notes_elems:
        try:
            notes_num += len(self.f_xps("//input[@name='%s']" % elem))
        except:
            pass
    i = self.input_num - self.input_req_num - notes_num - self.e
    if i > 0:
        self.logBad('%s полей без required' % i)