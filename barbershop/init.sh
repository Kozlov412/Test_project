#!/bin/bash
set -e  # Останавливает скрипт при любой ошибке

echo "====== Запуск скрипта инициализации ======"

# 1. Создание .env файла
echo "Создание .env файла..."
cat > .env << EOL
DEBUG=False
SECRET_KEY=your-secure-key-change-me
ALLOWED_HOSTS=*,localhost,127.0.0.1,.timeweb.ru
DATABASE_URL=sqlite:///db.sqlite3
EOL
echo ".env файл создан"

# 2. Выполнение миграций
echo "Выполнение миграций..."
python3 manage.py migrate
echo "Миграции выполнены успешно"

# 3. Создание суперпользователя
echo "Создание суперпользователя..."
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'kozlov67b@gmail.com', 'zaqwer765')
    print('Суперпользователь создан успешно')
else:
    print('Суперпользователь уже существует')
"
echo "Процесс создания суперпользователя завершен"

# 4. Загрузка данных
echo "Загрузка данных из дампа..."
python3 -Xutf8 manage.py loaddata data.json
echo "Данные загружены успешно"

# 5. Сбор статических файлов
echo "Сбор статических файлов..."
python3 manage.py collectstatic --noinput
echo "Статические файлы собраны успешно"

echo "====== Инициализация завершена успешно! ======"