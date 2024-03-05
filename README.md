Телеграм бот
Данный телеграм бот присылает уведомления о статусе проверки домашних работ ревьювером в рамках курса Яндекс Практикум.

Технологии
Python 3.7

Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

git clone git@github.com:GlebPogod1n/homework_bot.git
cd homework_bot/
Cоздать и активировать виртуальное окружение:

python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
Установить зависимости из файла requirements.txt:

pip install -r requirements.txt
Создаем .env файл с токенами:

PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>
Запускаем бота:

python homework.py
