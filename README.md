<img src="https://i.imgur.com/g3AtZrx.png"> 

>[English Readme](README-EN.md)

## Описание
Этот бот автоматически кликает, активирует бонусы, автоматически покупает самые выгодные апгрейды, есть поддержка нескольких аккаунтов и прокси одновременно.

Мой тг канал - https://t.me/+Dz4YR5Ho_701MjIy

## Установка
1. Скачиваем и распаковываем архив с гитхаба.
2. Установить Python 3.11
3. Открыть файл INSTALL.bat
4. Открыть файл .env в текстовом редакторе 
5. Вытащить API_ID и API_HASH (https://my.telegram.org/auth?to=apps)
6. Перейти к настрокам

## Настройки
| Настройка                            | Описание                                                                              |
|--------------------------------------|---------------------------------------------------------------------------------------|
| **API_ID / API_HASH**                | Вписываем данные, полученные ранее                                                    |
| **SLEEP_BY_MIN_ENERGY**              | Задержка при достижении минимальной энергии в секундах _(напр. 30)_                   |
| **AUTO_UPGRADE**                     | Улучшать ли пассивный заработок _(True / False)_                                      |
| **MAX_LEVEL**                        | Максимальный уровень прокачки апгрейда _(напр. 20)_                                   |
| **BALANCE_TO_SAVE**                  | Минимальный баланс для старта прокачки пассивного зароботка                           |
| **MIN_SIGNIFICANCE**                 | Минимальное соотношение прибыли к цене, чтобы купить карту. 0.1 = окупаемость 10 часов |
| **MULTIPLIER_FOR_CARDS_WITH_EXPIRE** | Мультипликатор для карт, время покупки которых ограничено                             |
| **PRIORITIZED_FIRST_LEVEL**          | Приоритизация покупки первого левела карты                                            |
| **APPLY_DAILY_ENERGY**               | Использовать ли ежедневный бесплатный буст энергии _(True / False)_                   |
| **APPLY_DAILY_TURBO**                | Использовать ли ежедневный бесплатный буст турбо _(True / False)_                     |
| **USE_PROXY_FROM_FILE**              | Использовать-ли прокси из файла `bot/config/proxies.txt` _(True / False)_             |
| **AUTO_CLAIM_DAILY_CIPHER**          | Авто прохождение шифра азбуки морзе.                                                  |
| **AUTO_FINISH_MINI_GAME**            | Авто прохождение мини-игры.                                                           |
| **AUTO_BUY_COMBO**                   | Авто покупка комбо карточек.                                                          |
| **AUTO_FINISH_BIKE_GAME**            | Авто завершение игры на bike 3d и получение ключей.                                   |
| **BUY_ALL_SKINS**                    | Покупать все скины в игре                                                             |

Пример заполнения файла с настройками

<img src="https://i.imgur.com/Aw7jNhJ.png">

## Запуск
1. Открыть командную строку (или терминал) в основной папке бота
2. Запустить main.py ```python3 main.py```
3. Создаём сессию
4. Снова запускаем main.py и начинаем фарм.

