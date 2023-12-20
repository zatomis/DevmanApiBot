import requests
import telegram as telegram
from environs import Env
from datetime import datetime, timedelta
import time
import os

def get_devman_statistic(api_key, params):
    url = "https://dvmn.org/api/long_polling/"
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def check_work(student_token, params, bot, tg_group_id):
    bot.send_message(chat_id=tg_group_id,
                     text=('Test'),
                     parse_mode=telegram.ParseMode.MARKDOWN_V2,
                     )
    while True:
        try:
            student_result = get_devman_statistic(student_token, params)
        except requests.exceptions.HTTPError as err:
            print(err.response.status_code)
            print(err.response.text)
        for message in student_result:
            print(message)



if __name__ == '__main__':
    env: Env = Env()
    env.read_env()
    request_time = 0
    token_student = env('STUDENT_TOKEN')
    telegram_bot = os.environ.get("TELEGRAMBOT_KEY", "ERROR")
    telegram_chanel = os.environ.get("TELEGRAMBOTGROUP", "ERROR")
    params = {}
    bot = telegram.Bot(token=telegram_bot)
    check_work(token_student, params, bot, telegram_chanel)
