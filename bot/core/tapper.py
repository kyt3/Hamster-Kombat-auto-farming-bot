import json
import asyncio
import operator
import base64
import random
import uuid
from time import time
from urllib.parse import unquote
from datetime import datetime, timedelta

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.utils.fingerprint import FINGERPRINT
from bot.utils.scripts import escape_html
from bot.exceptions import InvalidSession
from .headers import headers


class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            dialogs = self.tg_client.get_dialogs()
            async for dialog in dialogs:
                if dialog.chat and dialog.chat.username and dialog.chat.username == 'hamster_kombat_bot':
                    break

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('hamster_kombat_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    fls *= 2
                    logger.info(f"{self.session_name} | Sleep {fls}s")

                    await asyncio.sleep(fls)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://hamsterkombatgame.io/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def login(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> str:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/auth/auth-by-telegram-webapp',
                                              json={"initDataRaw": tg_web_data, "fingerprint": FINGERPRINT})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()
            access_token = response_json['authToken']

            return access_token
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Access Token: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def get_profile_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/sync',
                                              json={})
            response_text = await response.text()
            if response.status != 422:
                response.raise_for_status()

            response_json = json.loads(response_text)
            profile_data = response_json.get('clickerUser') or response_json.get('found', {}).get('clickerUser', {})

            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Profile Data: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def get_tasks(self, http_client: aiohttp.ClientSession) -> dict[str]:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/list-tasks',
                                              json={})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()
            tasks = response_json['tasks']

            return tasks
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Tasks: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def select_exchange(self, http_client: aiohttp.ClientSession, exchange_id: str) -> bool:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/select-exchange',
                                              json={'exchangeId': exchange_id})
            response_text = await response.text()
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while Select Exchange: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

            return False

    async def get_daily(self, http_client: aiohttp.ClientSession):
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/check-task',
                                              json={'taskId': "streak_days"})
            response_text = await response.text()
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Daily: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

            return False

    async def apply_boost(self, http_client: aiohttp.ClientSession, boost_id: str) -> bool:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/buy-boost',
                                              json={'timestamp': time(), 'boostId': boost_id})
            response_text = await response.text()
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while Apply {boost_id} Boost: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

            return False

    async def claim_daily_cipher(self, http_client: aiohttp.ClientSession, cipher: str) -> bool:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/claim-daily-cipher',
                                              json={'cipher': cipher})
            response_text = await response.text()
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while claim daily cipher '{cipher}': {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

            return False

    async def get_account_config(self, http_client: aiohttp.ClientSession) -> dict:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/config')
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while get account config: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def finish_mini_game(self, http_client: aiohttp.ClientSession, profile_data: dict):
        try:
            logger.info(f"{self.session_name} | <lr>Start claiming mini game...</lr> ")

            ## check timer.
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/start-keys-minigame')
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            seconds_to_guess = response_json["dailyKeysMiniGame"]["remainSecondsToGuess"]

            wait_time = random.randint(int(seconds_to_guess/2), int(seconds_to_guess - 5))

            if wait_time < 0:
                logger.error(f"[{self.session_name}] | Unable to claim mini game. Wait time less than 0")
                return

            logger.info(
                f"[{self.session_name}] | Mini-game will be completed in {wait_time} seconds..."
            )
            await asyncio.sleep(delay=wait_time)

            cipher = (
                    ("0" + str(random.randint(10000000000, 99999999999)))[:10]
                    + "|"
                    + str(profile_data["id"])
            )
            cipher_base64 = base64.b64encode(cipher.encode()).decode()

            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame',
                                              json={"cipher": cipher_base64})
            response_text = await response.text()
            response.raise_for_status()

            logger.success(f"{self.session_name} | Mini game claimed successfully.")
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while finishing mini game: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def get_combo_cards(self) -> dict:
        async with aiohttp.ClientSession() as http_client:
            response_text = ''
            try:
                response = await http_client.get(url='https://api21.datavibe.top/api/GetCombo')
                response_text = await response.text()
                response.raise_for_status()

                response_json = await response.json()

                return response_json
            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error while get combo cards: {error} | "
                             f"Response text: {escape_html(response_text)}...")
                await asyncio.sleep(delay=3)

    async def claim_daily_combo(self, http_client: aiohttp.ClientSession) -> bool:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/claim-daily-combo')
            response_text = await response.text()
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while claim daily combo: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)
            return False

    async def game_promo_login(self, http_client: aiohttp.ClientSession) -> str:
        response_text = ''
        try:
            logger.info(f"{self.session_name} | Login in promo API... ")

            cliend_id = str(datetime.timestamp(datetime.now())) + "-" + (str(random.randint(1000000000000000000, 9999999999999999999))[: 19])

            response = await http_client.post(url='https://api.gamepromo.io/promo/login-client',
                                              json={"appToken": "d28721be-fd2d-4b45-869e-9f253b554e50",
                                                    "clientId": f"{cliend_id}", "clientOrigin": "deviceid"})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            logger.success(f"{self.session_name} | Success login in promo API ")

            return response_json["clientToken"]
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while promo login: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def game_promo_register_event(self, http_client: aiohttp.ClientSession) -> bool:
        response_text = ''
        try:
            logger.info(f"{self.session_name} | Register promo event... ")

            response = await http_client.post(url='https://api.gamepromo.io/promo/register-event',
                                              json={"promoId": "43e35910-c168-4634-ad4f-52fd764a843f",
                                                    "eventId": f"{uuid.uuid4()}", "eventOrigin": "undefined"})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            logger.success(f"{self.session_name} | Successful register promo event")

            return response_json["hasCode"]
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while register promo event: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

            return False

    async def create_promo_code(self, http_client: aiohttp.ClientSession) -> str:
        response_text = ''
        try:
            logger.info(f"{self.session_name} | Creating promo code... ")

            response = await http_client.post(url='https://api.gamepromo.io/promo/create-code',
                                              json={"promoId": "43e35910-c168-4634-ad4f-52fd764a843f"})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            logger.success(f"{self.session_name} | Successful created promo code")

            return response_json["promoCode"]
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while register promo event: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def apply_promo(self, http_client: aiohttp.ClientSession, promo_code: str):
        response_text = ''
        try:
            logger.info(f"{self.session_name} | Apply promo code... ")

            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/apply-promo',
                                              json={"promoCode": f"{promo_code}"})
            response_text = await response.text()
            response.raise_for_status()

            logger.success(f"{self.session_name} | Successful applied promo code")
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while register promo event: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def finish_bike_game(self):
        async with aiohttp.ClientSession() as http_client:
            http_client.headers["Content-Type"] = f"application/json; charset=utf-8"
            http_client.headers["Host"] = f"api.gamepromo.io"

            client_token = await self.game_promo_login(http_client)
            http_client.headers["Authorization"] = f"Bearer {client_token}"

            code_available = False

            while not code_available:
                logger.info(f"{self.session_name} | Sleep 60 seconds before register event ")
                await asyncio.sleep(delay=60)
                code_available = await self.game_promo_register_event(http_client)

            promo_code = await self.create_promo_code(http_client)
            return promo_code

    async def get_promos(self, http_client: aiohttp.ClientSession) -> dict:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/get-promos',
                                              json={})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Upgrades: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def get_upgrades(self, http_client: aiohttp.ClientSession) -> dict:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/upgrades-for-buy',
                                              json={})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Upgrades: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def buy_upgrade(self, http_client: aiohttp.ClientSession, upgrade_id: str) -> bool:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/buy-upgrade',
                                              json={'timestamp': time(), 'upgradeId': upgrade_id})
            response_text = await response.text()
            if response.status != 422:
                response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while buying Upgrade: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

            return False

    async def get_boosts(self, http_client: aiohttp.ClientSession) -> list[dict]:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/boosts-for-buy', json={})
            response_text = await response.text()
            response.raise_for_status()

            response_json = await response.json()
            boosts = response_json['boostsForBuy']

            return boosts
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Boosts: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def send_taps(self, http_client: aiohttp.ClientSession, available_energy: int, taps: int) -> dict[str]:
        response_text = ''
        try:
            response = await http_client.post(url='https://api.hamsterkombatgame.io/clicker/tap',
                                              json={'availableTaps': available_energy, 'count': taps,
                                                    'timestamp': time()})
            response_text = await response.text()
            if response.status != 422:
                response.raise_for_status()

            response_json = json.loads(response_text)
            player_data = response_json.get('clickerUser') or response_json.get('found', {}).get('clickerUser', {})

            return player_data
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while Tapping: {error} | "
                         f"Response text: {escape_html(response_text)}...")
            await asyncio.sleep(delay=3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        turbo_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            tg_web_data = await self.get_tg_web_data(proxy=proxy)

            while True:
                try:
                    if time() - access_token_created_time >= 3600:
                        access_token = await self.login(http_client=http_client, tg_web_data=tg_web_data)

                    if not access_token:
                        continue

                    http_client.headers["Authorization"] = f"Bearer {access_token}"

                    access_token_created_time = time()

                    profile_data = await self.get_profile_data(http_client=http_client)
                    config_data = await self.get_account_config(http_client=http_client)

                    if not profile_data:
                        continue

                    if not config_data:
                        continue

                    exchange_id = profile_data.get('exchangeId')
                    if not exchange_id:
                        status = await self.select_exchange(http_client=http_client, exchange_id="bybit")
                        if status is True:
                            logger.success(f"{self.session_name} | Successfully selected exchange <y>Bybit</y>")

                    last_passive_earn = profile_data['lastPassiveEarn']
                    earn_on_hour = profile_data['earnPassivePerHour']

                    logger.info(f"{self.session_name} | Last passive earn: <g>+{last_passive_earn:,}</g> | "
                                f"Earn every hour: <y>{earn_on_hour:,}</y>")

                    available_energy = profile_data.get('availableTaps', 0)
                    balance = int(profile_data.get('balanceCoins', 0))

                    tasks = await self.get_tasks(http_client=http_client)

                    daily_task = tasks[-1]
                    rewards = daily_task['rewardsByDays']
                    is_completed = daily_task['isCompleted']
                    days = daily_task['days']

                    if is_completed is False:
                        status = await self.get_daily(http_client=http_client)
                        if status is True:
                            logger.success(f"{self.session_name} | Successfully get daily reward | "
                                           f"Days: <m>{days}</m> | Reward coins: {rewards[days - 1]['rewardCoins']}")

                    if settings.AUTO_CLAIM_DAILY_CIPHER is True:
                        if "dailyCipher" in config_data:
                            if not config_data["dailyCipher"]["isClaimed"]:
                                logger.info(f"{self.session_name} | <lr>Try claim daily cipher...</lr> ")
                                cipher = config_data["dailyCipher"]["cipher"]
                                cipher = cipher[:3] + cipher[4:]
                                cipher = cipher.encode("ascii")
                                cipher = base64.b64decode(cipher)
                                cipher = cipher.decode("ascii")

                                logger.info(f"{self.session_name} | Decoded cipher <ly>{cipher}</ly>, sending... ")

                                success = await self.claim_daily_cipher(http_client=http_client, cipher=cipher)

                                if success is True:
                                    logger.success(f"{self.session_name} | Successfully claimed cipher <y>{cipher}</y>")
                                else:
                                    logger.error(f"{self.session_name} | Not successful")
                            else:
                                logger.info(f"{self.session_name} | <ly>Daily cipher already claimed</ly>")

                        else:
                            logger.error(f"{self.session_name} | Not found daily cipher in config... ")

                    if settings.AUTO_FINISH_MINI_GAME is True:
                        if "dailyKeysMiniGame" in config_data:
                            if not config_data["dailyKeysMiniGame"]["isClaimed"]:

                                if config_data["dailyKeysMiniGame"]["remainSecondsToNextAttempt"] > 0:
                                    logger.info(f"{self.session_name} | Mini game on cooldown...")
                                else:
                                    await self.finish_mini_game(http_client=http_client, profile_data=profile_data)
                            else:
                                logger.info(f"{self.session_name} | <ly>Mini game already claimed</ly>")

                        else:
                            logger.error(f"{self.session_name} | Not found mini game keys in config... ")

                    if settings.AUTO_BUY_COMBO is True:
                        upgrades_data = await self.get_upgrades(http_client=http_client)
                        upgrades = upgrades_data['upgradesForBuy']
                        if not upgrades_data['dailyCombo']['isClaimed']:
                            combo_cards = await self.get_combo_cards()

                            cards = combo_cards['combo']
                            date = combo_cards['date']

                            available_combo_cards = [
                                data for data in upgrades
                                if data['isAvailable'] is True
                                   and data['id'] in cards
                                   and data['id'] not in upgrades_data['dailyCombo']['upgradeIds']
                                   and data['isExpired'] is False
                                   and data.get('cooldownSeconds', 0) == 0
                                   and data.get('maxLevel', data['level']) >= data['level']
                            ]

                            start_bonus_round = datetime.strptime(date, "%d-%m-%y").replace(hour=14)
                            end_bonus_round = start_bonus_round + timedelta(days=1)

                            if start_bonus_round <= datetime.now() < end_bonus_round:
                                common_price = sum([upgrade['price'] for upgrade in available_combo_cards])
                                need_cards_count = len(cards) - len(upgrades_data['dailyCombo']['upgradeIds'])
                                possible_cards_count = len(available_combo_cards)
                                is_combo_accessible = need_cards_count == possible_cards_count

                                if not is_combo_accessible:
                                    logger.info(f"{self.session_name} | "
                                                f"<lr>Daily combo is not applicable</lr>, you can only purchase {possible_cards_count} of {need_cards_count} cards")


                                logger.info(f"{self.session_name} | "
                                            f"<lr>Daily combo common price is </lr><ly>{common_price:,}</ly> coins")

                                if common_price < upgrades_data['dailyCombo']['bonusCoins'] and balance > common_price and is_combo_accessible:
                                    for upgrade in available_combo_cards:
                                        upgrade_id = upgrade['id']
                                        level = upgrade['level']
                                        price = upgrade['price']
                                        profit = upgrade['profitPerHourDelta']

                                        logger.info(
                                            f'{self.session_name} | '
                                            f'Sleep 5s before upgrade <lr>combo</lr> card <le>{upgrade_id}</le>'
                                        )

                                        await asyncio.sleep(delay=5)

                                        status = await self.buy_upgrade(
                                            http_client=http_client,
                                            upgrade_id=upgrade_id,
                                        )

                                        if status is True:
                                            earn_on_hour += profit
                                            balance -= price
                                            logger.success(
                                                f'{self.session_name} | '
                                                f'Successfully upgraded <le>{upgrade_id}</le> with price <lr>{price:,}</lr> to <m>{level}</m> lvl | '
                                                f'Earn every hour: <ly>{earn_on_hour:,}</ly> (<lg>+{profit:,}</lg>) | '
                                                f'Money left: <le>{balance:,}</le>'
                                            )

                                            await asyncio.sleep(delay=1)

                                    await asyncio.sleep(delay=2)

                                    status = await self.claim_daily_combo(
                                        http_client=http_client
                                    )
                                    if status is True:
                                        logger.success(
                                            f"{self.session_name} | Successfully claimed daily combo | "
                                            f"Bonus: <lg>+{upgrades_data['dailyCombo']['bonusCoins']}</lg>"
                                        )
                                else:
                                    logger.info(f"{self.session_name} | "
                                                f"<le>Decided not buy combo</le>")
                            else:
                                logger.info(f"{self.session_name} | "
                                            f"<lr>Waiting for combo from api...</lr>")

                        else:
                            logger.info(f"{self.session_name} | <ly>Combo already claimed</ly>")

                    if settings.AUTO_FINISH_BIKE_GAME is True:
                        promos_data = await self.get_promos(http_client=http_client)

                        try:
                            max_keys_per_day = int(promos_data["promos"][0]["keysPerDay"])
                            keys_remain = max_keys_per_day - promos_data["states"][0]["receiveKeysToday"]
                        except Exception:
                            logger.error(f"{self.session_name} | <lr>Something wrong with get promo response. Response: {promos_data}</lr>")
                            keys_remain = 0

                        if keys_remain > 0:
                            while keys_remain > 0:
                                promo_code = await self.finish_bike_game()
                                logger.info(f"{self.session_name} | Sleep 10 seconds before apply promo...")
                                await asyncio.sleep(delay=10)
                                await self.apply_promo(http_client,promo_code)
                                keys_remain -= 1
                        else:
                            logger.info(f"{self.session_name} | <ly>Bike game already claimed</ly>")

                    if settings.AUTO_UPGRADE is True and balance > settings.BALANCE_TO_SAVE:
                        resort = True
                        while resort:
                            upgrades = await self.get_upgrades(http_client=http_client)
                            upgrades = upgrades["upgradesForBuy"]

                            available_upgrades = [
                                data for data in upgrades
                                if data['isAvailable'] is True
                                   and data['isExpired'] is False
                                   and data.get('cooldownSeconds', 0) == 0
                                   and data.get('maxLevel', data['level']) >= data['level']
                                   # and (data.get('condition') is None)
                                        # or data['condition'].get('_type') != 'SubscribeTelegramChannel')
                            ]

                            queue = []

                            for upgrade in available_upgrades:
                                upgrade_id = upgrade['id']
                                level = upgrade['level']
                                price = upgrade['price']
                                current_profit = upgrade['currentProfitPerHour']
                                profit = upgrade['profitPerHourDelta']

                                significance = (profit + current_profit) / price if price > 0 else 0

                                if balance - price < settings.BALANCE_TO_SAVE:
                                    continue

                                # logger.info(f"{self.session_name} | <y>{upgrade}</y>")

                                if upgrade.get('expiresAt') is None:
                                    if significance > settings.MIN_SIGNIFICANCE:
                                        queue.append([upgrade_id, significance, level, price, profit, current_profit, upgrade['name']])
                                else:
                                    date_expires = datetime.strptime(upgrade['expiresAt'],"%Y-%m-%dT%H:%M:%S.%fZ")
                                    date_now = datetime.now()
                                    timediff = date_expires - date_now
                                    # logger.info(f"{self.session_name} | <y>{upgrade['name']}</y> expires in <y>{timediff.total_seconds()}</y>")
                                    if timediff.total_seconds()/3600 > 2*(100/(significance*100)):
                                        queue.append([upgrade_id, significance, level, price, profit, current_profit, upgrade['name']])

                            queue.sort(key=operator.itemgetter(1), reverse=True)

                            if len(queue) == 0:
                                break

                            count = 0
                            for upgrade in queue:
                                if balance > upgrade[3] and upgrade[2] <= settings.MAX_LEVEL:
                                    logger.info(f"{self.session_name} | Sleep 5s before upgrade <e>{upgrade[6]}</e>")
                                    await asyncio.sleep(delay=5)

                                    status = await self.buy_upgrade(http_client=http_client, upgrade_id=upgrade[0])

                                    if status is True:
                                        earn_on_hour += upgrade[4]
                                        balance -= upgrade[3]
                                        logger.success(
                                            f"{self.session_name} | "
                                            f"Successfully upgraded <e>{upgrade[6]}</e> to <m>{upgrade[2]}</m> lvl | "
                                            f"Earn every hour: <y>{earn_on_hour:,}</y> (<g>+{upgrade[4]:,}--->{upgrade[4]+upgrade[5]:,}</g>) | "
                                            f"Price <y>{upgrade[3]:,}</y> | "
                                            f"Balance <e>{balance:,}</e>")

                                        await asyncio.sleep(delay=1)
                                        if balance < settings.BALANCE_TO_SAVE:
                                            resort = False
                                        break

                                count += 1
                                if count == 10 or count == len(queue) or balance < settings.BALANCE_TO_SAVE:
                                    resort = False
                                    break

                    earn_for_tap = profile_data['level'] + profile_data['boosts']['BoostEarnPerTap']['level']
                    while available_energy > earn_for_tap:

                        taps = int(available_energy / earn_for_tap)
                        sleep_between_clicks = taps / 10

                        logger.info(f"{self.session_name} | Sleep before sending taps {sleep_between_clicks}s")
                        await asyncio.sleep(delay=sleep_between_clicks)

                        if taps > 0:
                            player_data = await self.send_taps(http_client=http_client,
                                                               available_energy=available_energy,
                                                               taps=taps)

                            if not player_data:
                                continue

                            available_energy = player_data.get('availableTaps', 0)
                            new_balance = int(player_data.get('balanceCoins', 0))
                            calc_taps = new_balance - balance
                            balance = new_balance
                            total = int(player_data.get('totalCoins', 0))
                            earn_on_hour = player_data['earnPassivePerHour']

                            logger.success(f"{self.session_name} | Successful tapped! | "
                                           f"Balance: <c>{balance:,}</c> (<g>+{calc_taps}</g>) | "
                                           f"Earn every hour: <y>{earn_on_hour:,}</y> | Total: <e>{total:,}</e>")


                    boosts = await self.get_boosts(http_client=http_client)
                    energy_boost = next((boost for boost in boosts if boost['id'] == 'BoostFullAvailableTaps'), {})

                    if (settings.APPLY_DAILY_ENERGY is True
                            and available_energy < earn_for_tap
                            and energy_boost.get("cooldownSeconds", 0) == 0
                            and energy_boost.get("level", 0) <= energy_boost.get("maxLevel", 0)):
                        logger.info(f"{self.session_name} | Sleep 5s before apply energy boost")
                        await asyncio.sleep(delay=5)

                        status = await self.apply_boost(http_client=http_client, boost_id="BoostFullAvailableTaps")
                        if status is True:
                            logger.success(f"{self.session_name} | Successfully apply energy boost")

                            await asyncio.sleep(delay=1)

                            continue
                    if available_energy < earn_for_tap:
                        logger.info(f"{self.session_name} | Minimum energy reached: {available_energy}")
                        logger.info(f"{self.session_name} | Sleep {settings.SLEEP_BY_MIN_ENERGY}s")

                        await asyncio.sleep(delay=settings.SLEEP_BY_MIN_ENERGY)
                        continue

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)

                else:
                    sleep_between_clicks = settings.SLEEP_BY_MIN_ENERGY

                    logger.info(f"Sleep {sleep_between_clicks}s")
                    await asyncio.sleep(delay=sleep_between_clicks)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
