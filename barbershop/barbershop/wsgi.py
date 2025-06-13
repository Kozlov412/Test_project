"""
WSGI config for barbershop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Добавим отладочные сообщения
print("Загрузка WSGI приложения...")
sys.stdout.flush()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')

try:
    application = get_wsgi_application()
    print("WSGI приложение успешно загружено")
    sys.stdout.flush()
except Exception as e:
    print(f"Ошибка при загрузке WSGI приложения: {e}", file=sys.stderr)
    sys.stderr.flush()
    raise