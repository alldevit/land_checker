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
**3**. Скачиваем [chromedriver](http://chromedriver.chromium.org/downloads "Chromedriver"), указываем путь до него в файле `config.py`

**4**. Указываем реквизиты доступа к LeadRock.com в `config.py`

**5**. При первом запуске необходимо авторизоваться в Лидроке

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
При отсутствии track_url, будет использован стандартный track_url из файла `config.py`. В этом случае проверка отправки лида
будет осуществлена через оффер `v2 test integration`.

При необходимости проверки работы простой интеграции (например, в задачах для баеров) вместо track_url необходимо указать `0`, в этом случае подстановки track_url происходить не будет:
```
http://buyer.host/ 0
```

- Лог последней проверки сохраняется в `log_latest.log`
- При очередном запуске скрипта содержимое `log_latest.log` переносится в `log_full.log`
- Выявленные несоответствия языка элементов вносятся в `log_lang.log`

Вывод результатов доступен в двух форматах - полном и сокращённом. Сокращенный активируется установкой `True` для параметра `SILENT_MODE` в `config.py`, при этом в log_full.log всегда записывается полный вывод.

## Проверки для лендингов
- определение языка лендинга
- соответствие языка:
  - всех видимых элементов
  - содержимого мета-тегов `keywords` и `description`
  - содержимого `title`
  - страницы с политикой
  - конфирма
- наличие юрлица
- политика конфидециальности
  - наличие ссылки
  - открытие в новой вкладке
  - доступность страницы
- соответствие телефонного кода языку (ГЕО)
- метод отправки форм (POST, GET)
- наличие кнопок `submit` в каждой форме
- наличие обязательных полей name и phone во всех формах
- наличие `required` у обязательных полей
- вывод количества необязательных полей
- коллбэк
- вшитый/динамический `fbpixel` на лендинге и конфирме
- события `PageView` и `Lead` на лендинге и конфирме
- отправка лида
- упоминание отправки почтой на конфирме
- проверка отправки лида

## Проверки для прелендингов
- определение языка прелендинга
- соответствие языка:
  - всех видимых элементов
  - содержимого мета-тегов `keywords` и `description`
  - содержимого `title`
- анализ ссылок
