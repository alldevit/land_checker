# Проверка required для полей
# Считаем поля, считаем такие же поля с required, сравниваем количество
def inputs_required(self):
    if self.is_3_stage_form:
        self.driver.execute_script('salvatoreGannacci()')
    e = 0
    s = ''
    field_names = [
        'name',
        'phone',
        'other[address]',
        'other[city]',
        'other[zipcode]',
        'other[postcode]',
        'other[pcode]',
        'other[quantity]',
        'other[address2]',
        'other[index]'
        ]
        
    for elem in field_names:
        elem_num = len(self.f_xps("//input[@name='%s']" % elem))
        if elem_num > 0:
            elem_req_num = len(self.f_xps("//input[@name='%s' and @required]" % elem))
            if elem_num > elem_req_num:
                s += ' ' + elem
                e = e + elem_num - elem_req_num
    self.e = e
    if len(s) > 0:
        self.logBad('пропущен required для %s полей: %s' % (e, s))