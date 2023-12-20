import requests
from environs import Env
from datetime import datetime, timedelta
import time
import os

def get_devman_statistic(api_key, time):
    url = "https://dvmn.org/api/long_polling/"
    headers = {'Authorization': f'Token {api_key}'}
    payload = {'timestamp': {time}}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    env: Env = Env()
    env.read_env()
    token = env('STUDENT_TOKEN')
    request_time = 0
    while True:
        try:
            response = get_devman_statistic(token, request_time)
        except requests.exceptions.HTTPError as err:
            print(err.response.status_code)
            print(err.response.text)
        for message in response:
            print(message)

