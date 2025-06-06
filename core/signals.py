import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from core.models import Order
from core.telegram_bot import process_order

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def order_created_signal(sender, instance, created, **kwargs):
    """
    Сигнал при создании заявки
    """
    if created:
        logger.info(f"Создана новая заявка: {instance.id}")
        process_order(instance, is_created=True)


@receiver(m2m_changed, sender=Order.services.through)
def services_changed_signal(sender, instance, action, pk_set, **kwargs):
    """
    Сигнал при изменении услуг
    """
    if action == 'post_add' and pk_set:
        logger.info(f"Добавлены услуги к заявке {instance.id}: {pk_set}")
        process_order(instance, is_created=False)