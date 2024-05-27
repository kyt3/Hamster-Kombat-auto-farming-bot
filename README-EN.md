<img src="https://i.imgur.com/g3AtZrx.png"> 

[>Русский Readme](README.md)
## Description
This bot automatically clicks, activates bonuses, automatically buys the most profitable upgrades, supports multiaccounts and proxies.
My tg channel - https://https://t.me/+Dz4YR5Ho_701MjIy

## Installation
1. Download file from github.
2. Download Python 3.11
3. Open cmd (or terminal)
4. Open INSTALL.bat
5. Open .env file 
6. Get API_ID and API_HASH (https://my.telegram.org/auth?to=apps)

## Settings
| Setting                  | Description                                                                                  |
|--------------------------|------------------------------------------------------------------------------------------    |
| **API_ID / API_HASH**    | Platform data from which to launch a Telegram session _(stock - Android)_                    |
| **MIN_AVAILABLE_ENERGY** | Minimum amount of available energy, upon reaching which there will be a delay _(example 10)_ |
| **SLEEP_BY_MIN_ENERGY**  | Delay when reaching minimum energy in seconds _(example 30)_                                 |
| **AUTO_UPGRADE**         | Whether to upgrade the passive earn _(True / False)_                                         |
| **MAX_LEVEL**            | Maximum upgrade level _(example 20)_                                                         |
| **APPLY_DAILY_ENERGY**   | Whether to use the daily free energy boost _(True / False)_                                  |
| **APPLY_DAILY_TURBO**    | Whether to use the daily free turbo boost _(True / False)_                                   |
| **RANDOM_CLICKS_COUNT**  | Random number of taps _(eg [10,200])_                                                        |
| **SLEEP_BETWEEN_TAP**    | Random delay between taps in seconds _(eg [10,80])_                                          |
| **USE_PROXY_FROM_FILE**  | Whether to use proxy from the `bot/config/proxies.txt` file (True / False)                   |

Example

<img src="https://i.imgur.com/Aw7jNhJ.png">

## Starting
1. Open cmd (or terminal)
2. Start main.py ```python3 main.py```
3. Create session
4. Reopen main.py and start farming.

