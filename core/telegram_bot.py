import os
import asyncio
import logging
import time
from django.conf import settings
from django.urls import reverse
import telegram
from telegram.constants import ParseMode

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кэш для хранения заявок, ожидающих добавления услуг
PENDING_ORDERS = {}

async def send_telegram_notification(chat_id, message):
    """
    Асинхронно отправляет сообщение через Telegram API с HTML форматированием
    """
    token = settings.TELEGRAM_BOT_TOKEN
    
    try:
        bot = telegram.Bot(token=token)
        await bot.send_message(
            chat_id=chat_id, 
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False  # Разрешаем предпросмотр URL
        )
        logger.info("Сообщение успешно отправлено")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке HTML-сообщения: {e}")
        # Пробуем отправить без форматирования
        try:
            bot = telegram.Bot(token=token)
            await bot.send_message(
                chat_id=chat_id, 
                text=message.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', ''),
                disable_web_page_preview=False
            )
            logger.info("Сообщение отправлено без HTML форматирования")
            return True
        except Exception as e2:
            logger.error(f"Повторная ошибка при отправке уведомления: {e2}")
            return False

def send_message(message):
    """
    Отправляет сообщение в Telegram
    """
    try:
        chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
        return asyncio.run(send_telegram_notification(chat_id, message))
    except Exception as e:
        logger.error(f"Ошибка при подготовке отправки уведомления: {e}")
        return False

def get_admin_url(instance):
    """
    Формирует URL для доступа к объекту в админке
    """
    admin_path = reverse('admin:core_order_change', args=[instance.id])
    return f"{settings.SITE_URL}{admin_path}"

def clean_client_name(name):
    """
    Очищает имя клиента от технических префиксов и суффиксов
    """
    # Удаляем префикс "Заказ XX - " если он есть
    if " - " in name:
        parts = name.split(" - ", 1)
        if parts[0].startswith("Заказ"):
            name = parts[1]
    
    # Удаляем суффикс в скобках, например "(not_approved)"
    if "(" in name and ")" in name:
        name = name.split("(")[0].strip()
    
    return name

def format_order_message(instance, with_services=True):
    """
    Форматирует красивое информативное сообщение о заявке
    """
    # Получаем данные заявки
    client_name_raw = str(instance)
    client_name = clean_client_name(client_name_raw)  # Очищаем имя от префикса и статуса
    phone = getattr(instance, 'phone', '')
    comment = getattr(instance, 'comment', '')
    
    # Получаем URL админки
    admin_url = get_admin_url(instance)
    
    # Заголовок сообщения
    message = f"""
🆕 <b>НОВАЯ ЗАЯВКА #{instance.id}</b>

👤 <b>Клиент:</b> <i>{client_name}</i>

📱 <b>Телефон:</b> <a href="tel:{phone}">{phone}</a>

📝 <b>Комментарий:</b> <i>{comment or '—'}</i>
"""
    
    # Добавляем информацию об услугах, если нужно и они есть
    if with_services and hasattr(instance, 'services') and instance.services.exists():
        services_list = []
        total_price = 0
        
        for service in instance.services.all():
            service_name = getattr(service, 'name', str(service))
            service_price = getattr(service, 'price', 0)
            services_list.append(f"• <i>{service_name}</i> — <b>{service_price}</b> ₽")
            total_price += service_price
        
        services_text = "\n".join(services_list)
        
        # Используем красивое форматирование для списка услуг
        message += f"""
✂️ <b>ВЫБРАННЫЕ УСЛУГИ:</b>
{services_text}

💰 <b>Общая стоимость:</b> <b>{total_price}</b> ₽
"""
    
    # Добавляем дату создания с красивым форматированием
    created_at = getattr(instance, 'created_at', None)
    if created_at and hasattr(created_at, 'strftime'):
        message += f"\n🗓 <b>Дата создания:</b> <i>{created_at.strftime('%d.%m.%Y %H:%M')}</i>"
    
    # Добавляем просто ссылку на админку, без лишних заголовков
    message += f"""

🔗 <a href="{admin_url}">Открыть в админ-панели</a>

<i>Steel Beard Management System</i> 🧔✂️
"""
    
    return message

def process_order(instance, is_created=False):
    """
    Обрабатывает заявку и решает, когда отправлять уведомление
    
    :param instance: Объект заявки
    :param is_created: True, если заявка только что создана
    """
    # Если заявка только создана, добавляем в ожидающие
    if is_created:
        PENDING_ORDERS[instance.id] = {
            'instance': instance,
            'timestamp': time.time(),
            'has_services': False
        }
        # Делаем небольшую задержку, чтобы дать возможность добавить услуги
        # Через 2 секунды проверим, были ли добавлены услуги
        return
    
    # Если добавлены услуги к существующей заявке
    if instance.id in PENDING_ORDERS:
        # Если прошло меньше 5 секунд с момента создания, просто помечаем, что есть услуги
        if time.time() - PENDING_ORDERS[instance.id]['timestamp'] < 5:
            PENDING_ORDERS[instance.id]['has_services'] = True
            return
        
        # Если прошло больше 5 секунд, отправляем сообщение и удаляем из ожидающих
        order_data = PENDING_ORDERS.pop(instance.id)
        message = format_order_message(instance, True)
        send_message(message)
        return
    
    # Если это не новая заявка и не ожидающая, просто отправляем сообщение с услугами
    message = format_order_message(instance, True)
    send_message(message)

def check_pending_orders():
    """
    Проверяет ожидающие заявки и отправляет уведомления по тем, 
    что ждут больше 5 секунд
    """
    current_time = time.time()
    to_remove = []
    
    for order_id, data in PENDING_ORDERS.items():
        # Если заявка ожидает больше 5 секунд
        if current_time - data['timestamp'] > 5:
            instance = data['instance']
            with_services = data['has_services']
            # Отправляем сообщение
            message = format_order_message(instance, with_services)
            send_message(message)
            # Помечаем для удаления
            to_remove.append(order_id)
    
    # Удаляем обработанные заявки
    for order_id in to_remove:
        PENDING_ORDERS.pop(order_id, None)

# Запускаем проверку ожидающих заявок каждые 5 секунд
def start_checking_pending_orders():
    """
    Запускает периодическую проверку ожидающих заявок
    """
    import threading
    
    def check_loop():
        while True:
            try:
                check_pending_orders()
                time.sleep(5)
            except Exception as e:
                logger.error(f"Ошибка в цикле проверки ожидающих заявок: {e}")
    
    # Запускаем в отдельном потоке
    checker_thread = threading.Thread(target=check_loop, daemon=True)
    checker_thread.start()
    logger.info("Запущен фоновый процесс проверки ожидающих заявок")

# Запускаем проверку при импорте модуля
start_checking_pending_orders()