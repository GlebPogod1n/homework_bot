import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from json.decoder import JSONDecodeError
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s')


def check_tokens() -> bool:
    """Проверяет доступность переменных."""
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def send_message(bot, message):
    """Отправляет сообщение."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Успешная отправка сообщения.')
    except telegram.TelegramError:
        logger.error('Сообщения не отправляются')


def get_api_answer(timestamp):
    """Выполняет запрос к API."""
    timestamp = timestamp or int(time.time())
    params = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={"from_date": timestamp}
    )
    try:
        homework_statuses = requests.get(**params)
    except requests.exceptions.RequestException as error:
        logger.error(f"Ошибка при запросе к API: {error}")
    else:
        if homework_statuses.status_code != HTTPStatus.OK:
            error_message = "Статус страницы не равен 200"
            raise requests.HTTPError(error_message)
        try:
            return homework_statuses.json()
        except JSONDecodeError:
            logger.error("N'est pas JSON")


def check_response(response):
    """Проверяем ответ API."""
    if not isinstance(response, dict):
        raise TypeError('API возвращает не словарь.')
    if 'homeworks' not in response:
        raise KeyError('Не найден ключ homeworks.')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('API возвращает не список.')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает статус работы."""
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if not verdict:
        message_verdict = "Такого статуса нет в словаре"
        raise KeyError(message_verdict)
    if homework_status not in HOMEWORK_VERDICTS:
        message_homework_status = "Такого статуса не существует"
        raise KeyError(message_homework_status)
    if "homework_name" not in homework:
        message_homework_name = "Такого имени не существует"
        raise KeyError(message_homework_name)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Ошибка в получении токенов!')
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_message = ''

    while True:
        try:
            if type(timestamp) is not int:
                raise SystemError('В функцию передана не дата')
            response = get_api_answer(timestamp)
            response = check_response(response)

            if len(response) > 0:
                homework_status = parse_status(response[0])
                if homework_status is not None:
                    send_message(bot, homework_status)
            else:
                logger.debug('нет новых статусов')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != old_message:
                bot.send_message(TELEGRAM_CHAT_ID, message)
                old_message = message
        finally:
            timestamp = int(time.time())
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
