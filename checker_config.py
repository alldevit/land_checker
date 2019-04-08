import os

track_url = "URL-C53EA-0260C" # трек-урл с левого оффера, нужен в служебных целях
fbpixel = "123123123123"
driver_path = "C:/Users/ed/testing/chromedriver/chromedriver.exe"
mini_log = "log_latest.log"
full_log = "log_full.log"
lang_log = "log_lang.log"
post_log = "log_post.log"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/ed/testing/check_landings/g.json"
default_translate_method = "lib" # {lib, cloud, api}