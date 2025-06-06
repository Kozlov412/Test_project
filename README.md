Steel Beard Barbershop
Проект системы управления заявками для барбершопа с интеграцией Telegram-уведомлений.

Функциональность
Создание и управление заявками клиентов
Каталог мастеров и услуг
Автоматические уведомления в Telegram при новых заявках

Настройка проекта
1. Клонировать репозиторий
bash
git clone https://github.com/your-username/barbershop.git
cd barbershop

2. Установка с Poetry
bash
# Установка Poetry (если не установлен)
# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# MacOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell

3. Альтернативная установка через pip
bash
# Создание виртуального окружения
python -m venv venv

# Активация
# Windows
venv\Scripts\activate
# MacOS/Linux
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

4. Настройка переменных окружения
Создайте файл .env на основе .env.example:

bash
cp .env.example .env
# Затем отредактируйте .env и добавьте нужные значения

5. Настройка базы данных
bash
# Применение миграций
poetry run python manage.py migrate

# Создание суперпользователя
poetry run python manage.py createsuperuser

6. Запуск сервера
bash
poetry run python manage.py runserver

Инструкция для настройки Telegram-бота
Создайте бота через @BotFather и получите токен
Добавьте бота в контакты и отправьте ему сообщение
Узнайте ваш Chat ID через бота @userinfobot
Укажите полученные данные в файле .env:

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_CHAT_ID=your_chat_id
SITE_URL=http://127.0.0.1:8000

Использование
После настройки проекта:

Создавайте и управляйте заявками через админ-панель Django: http://127.0.0.1:8000/admin/
При создании новой заявки администратор получит уведомление в Telegram
После добавления услуг к заявке придет полное уведомление со списком выбранных услуг
Технологии
Django
Python Telegram Bot
Poetry для управления зависимостями
SQLite (для разработки)