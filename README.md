# land_checker

## Установка
**1**. Обновляем **pip** до последней версии
```bash
python -m pip install --upgrade pip
```
**2**. Устанавливаем необходимые модули
```bash
pip install selenium langdetect googletrans google-cloud-translate requests
```
**3**. Указываем пути до webdriver'а (по-умолчанию - `chromedriver.exe`) и `g.json` в файле `checker_config.py`

**4**. Указываем реквизиты доступа к LeadRock.com в `cookie_saver.py`

**5**. Запускаем `cookie_saver.py` и дожидаемся появления файла `cookies.pkl`

## Использование
В директории со скриптом создаем файл `landings.txt` и указываем в нем список лендингов для проверки в формате:
```
http://landing.one/
https://landing.two/it/1/
http://landing.three/es/
```
При наличии сгенерированных track_url для данной задачи/оффера, указываем их для автоматической отправки и проверки лида:
```
http://landing.one/ URL-C53EA-0260C
https://landing.two/it/1/ URL-B84AE-7429B
http://landing.three/es/
```
При отсутствии track_url, будет использован стандартный track_url из файла `checker_config.py`. В этом случае проверка отправки лида
будет осуществлена через оффер `v2 test integration`.

- Лог последней проверки сохраняется в `log_latest.log`
- При очередном запуске скрипта содержимое `log_latest.log` переносится в `log_full.log`
- Выявленные несоответствия языка элементов вносятся в `log_lang.log`

При проверке результатов тестирования следует обратить внимание не пункты, помеченые минусом ` - `:
```
- юрлицо не указано
- ссылка на policy отсутствует
```
