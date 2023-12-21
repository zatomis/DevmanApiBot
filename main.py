from textwrap import dedent

import requests
import telegram as telegram
from environs import Env
import time
import os

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
        except requests.exceptions.ConnectionError:
            time.sleep(30)
        else:
            if student_result['status'] == 'timeout':
                timestamp_to_request = student_result['timestamp_to_request']
                params = {
                    'timestamp': timestamp_to_request,
                }
            else:
                for current_review in student_result['new_attempts']:
                    time.sleep(5)
                    if current_review['is_negative']:
                        bot.send_message(chat_id=tg_group_id,
                                         text=f'Pаботa ⛔️ *{current_review["lesson_title"]}*\nК сожалению, в работе нашлись ошибки\n[Ссылка на работу]({current_review["lesson_url"]})')
                                         # text=f'{current_review["lesson_title"]}')
                    else:
                        bot.send_message(chat_id=tg_group_id,
                                         text=f'Pаботa ✅ *{current_review["lesson_title"]}*\n Принята.\n[Ссылка на работу]({current_review["lesson_url"]})')

                        # text=dedent(f"""
                        #                  Преподаватель проверил работу *"{current_review["lesson_title"]}"*\
                        #                  Преподавателю все понравилось, можно приступать к следующему уроку\
                        #                  """),
                        #                  parse_mode=telegram.ParseMode.MARKDOWN_V2,
                        #                  )



if __name__ == '__main__':
    env: Env = Env()
    env.read_env()
    request_time = 0
    token_student = env('STUDENT_TOKEN')
    telegram_bot = os.environ.get("TELEGRAMBOT_KEY", "ERROR")
    telegram_chanel = os.environ.get("TELEGRAMBOTGROUP", "ERROR")
    params = {'timestamp': 0,}
    bot = telegram.Bot(token=telegram_bot)
    check_work(token_student, params, bot, telegram_chanel)
