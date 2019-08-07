import time, random
from datetime import datetime

from config import Config
from utils import Utils, Driver
from checks.all_imports import *


Utils.log_restart()
lands = Utils.get_lands()

if not Utils.cookies_exist():
    driver = Driver(images=True, headless=False)
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
    if 'leadrocktest.com' in runner.link:
        runner.link = runner.link.replace('://', '://%s:%s@' % (runner.SERVER_LOGIN, runner.SERVER_PASS))
        
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