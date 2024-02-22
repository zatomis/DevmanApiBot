import logging

import requests
import telegram as telegram
from environs import Env
import time
import os
from requests import HTTPError, ConnectionError

logger = logging.getLogger(__name__)


class BotLogsHandler(logging.Handler):

    def __init__(self, bot, admin_chat_id):
        self.bot = bot
        self.admin_chat_id = admin_chat_id
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=log_entry,
        )


def get_devman_statistic(api_key, params):
    url = "https://dvmn.org/api/long_polling/"
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def check_work(student_token, params, bot, tg_group_id):
    while True:
        try:
            student_result = get_devman_statistic(student_token, params)
        except requests.exceptions.ReadTimeout:
            continue
        except HTTPError as http_error:
            logger.warning(f"\nHTTP error occurred: {http_error}")
            time.sleep(30)
        except ConnectionError as connection_error:
            logger.warning(f"\nConnection error occurred: {connection_error}")
            time.sleep(30)
        else:
            if student_result['status'] == 'timeout':
                timestamp_to_request = student_result['timestamp_to_request']
                params = {
                    'timestamp': timestamp_to_request,
                }
            else:
                for current_review in student_result['new_attempts']:
                    if current_review['is_negative']:
                        bot.send_message(chat_id=tg_group_id,
                                         text=f'Pаботa ⛔️ *{current_review["lesson_title"]}*\nК сожалению, в работе нашлись ошибки\n[Ссылка на работу]({current_review["lesson_url"]})')
                    else:
                        bot.send_message(chat_id=tg_group_id,
                                         text=f'Pаботa ✅ *{current_review["lesson_title"]}*\n Принята.\n[Ссылка на работу]({current_review["lesson_url"]})')


if __name__ == '__main__':
    env: Env = Env()
    env.read_env()
    request_time = 0
    token_devman = env('DEVMAN_STUDENT_TOKEN')
    telegram_bot = os.environ.get("TELEGRAMBOT_KEY", "ERROR")
    telegram_chanel = os.environ.get("TELEGRAMBOTGROUP", "ERROR")
    admin_chat_id = os.environ.get("ADMINTELEGRAM", telegram_chanel)
    params = {'timestamp': 0, }
    bot = telegram.Bot(token=telegram_bot)

    logger.setLevel(logging.INFO)
    log_handler = BotLogsHandler(bot, admin_chat_id)

    format = '%(filename)s: [%(lineno)d] - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
    formatter = logging.Formatter(format)
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.INFO)

    logger.addHandler(log_handler)
    logger.info('TBot started...')
    check_work(token_devman, params, bot, telegram_chanel)
