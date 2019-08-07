from random import randint

def info(self):

    try:
        self.driver.execute_script('uusyuka()')
        self.is_poll = True
    except:
        self.is_poll = False
        pass
    
    try:
        self.driver.execute_script('salvatoreGannacci()')
        self.is_3_stage_form = True
    except:
        self.is_3_stage_form = False
        pass

    self.form_num       = len(self.f_xps("//form[input or *//input]"))
    self.action_num     = len(self.f_xps("//form[(input or *//input) and @action]"))
    self.post_num       = len(self.f_xps("//form[@method='POST' or @method='post'][input or *//input]"))
    self.get_num        = len(self.f_xps("//form[@method='GET' or @method='get']"))
    self.input_num      = len(self.f_xps("(//input[@type='text'])")) + len(self.f_xps("(//input[@type='tel'])"))
    self.input_req_num  = len(self.f_xps("(//input[@type='text' and @required])")) + len(self.f_xps("(//input[@type='tel' and @required])"))
    self.submit_num     = len(self.f_xps("//*[@type='submit']"))
    self.req_num        = len(self.f_xps("//input[@required]"))
    self.name_num       = len(self.f_xps("//input[@name='name']"))
    self.phone_num      = len(self.f_xps("//input[@name='phone']"))
    self.links_num      = len(self.f_tags("a"))
    self.anchors_num    = len(self.f_xps("//*[contains(@href, '#')]"))
    self.email_num      = len(self.f_xps("//input[contains(@name, 'email')]"))
    self.wheel_exist    = len(self.f_xps(".//div[contains(@class, 'wheel')]/span[contains(@class, 'cursor-text')]"))
    self.search_num     = len(self.f_xps("//form[contains(@class, 'search')]"))
    self.iframe_num     = len(self.f_xps("//iframe")) - len(self.f_xps("//iframe[contains(@name, '_ym_native')]")) - len(self.f_xps("//iframe[contains(@name, 'ym-native-frame')]"))
    self.wf_frame_num   = len(self.f_xps("//iframe[contains(@src, 'offerteonline2017.com')]")) + len(self.f_xps("//iframe[contains(@src, 'worldfilia.net')]"))
    self.source         = self.driver.page_source
    self.page_text      = self.f_tag("body").text
    self.lead           = randint(1000, 9999)