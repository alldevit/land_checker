import time, random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import Config
from utils import Utils, Lang
from checks.all_imports import *

class Driver(Config, Utils, Lang):
    def __init__(self):
        options = Options()
        options.add_argument('log-level=2')
        options.add_argument("--start-maximized")
        if self.HEADLESS_MODE:
            options.add_argument('--headless')
        prefs = {'profile.managed_default_content_settings.images':2}
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(self.DRIVER_PATH, options=options)
        self.driver.delete_all_cookies()
        self.log_bad_list = []

Utils.log_restart()
lands = Utils.get_lands()

if not Utils.cookies_exist():
    driver = Driver()
    driver.cookie_saver()
    driver.stop()


for land in lands:

    runner = Driver()
    runner.land = land[0]
    runner.track_url = land[1]


    if runner.track_url == '0':
        runner.link = '%s?fbpixel=%s' % (runner.land, runner.FBPIXEL)
    else:
        runner.link = '%s?track_url=%s&fbpixel=%s' % (runner.land, runner.track_url, runner.FBPIXEL)
        
    runner.log(datetime.strftime(datetime.now(), '%Y.%m.%d %H:%M:%S'))
    runner.log('%s %s' % (runner.land, runner.track_url), force=True)

    runner.page_open(runner.link)
    if page_exist(runner):
        info(runner)
        if is_land(runner):
            lang_main(runner)
            lang_elements(runner)
            title(runner)
            lang_meta(runner)
            contacts(runner)
            if policy_link(runner):
                policy_blank(runner)
                policy_exist(runner)
                policy_lang(runner)
            runner.page_open(runner.link)
            anchors(runner)
            fbpixel(runner, 'ленде')
            if not wf_frame(runner):
                callback(runner)
                phone_code(runner)
                forms_post(runner)
                forms_get(runner)
                forms_action(runner)
                submit(runner)
                inputs_exist(runner)
                inputs_required(runner)
                inputs_nonrequired(runner)
                input_email(runner)
                if lead(runner):
                    fbpixel(runner, 'thankyou')
                    lang_confirm(runner)
                    shipping_post(runner)
                    lead_check(runner)
        else:
            lang_main(runner)
            lang_elements(runner)
            title(runner)
            lang_meta(runner)
            pre_links(runner)
    result(runner)
    runner.stop()