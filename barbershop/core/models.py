from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Статусы заказов
STATUS_CHOICES = [
    ("not_approved", "Не подтвержден"),
    ("approved", "Подтвержден"),
    ("in_progress", "В процессе"),
    ("completed", "Выполнен"),
    ("cancelled", "Отменен"),
]

class Service(models.Model):
    """Модель услуги в барбершопе."""
    name = models.CharField(max_length=200, verbose_name="Название", db_index=True)  # индекс на название
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration = models.PositiveIntegerField(verbose_name="Длительность", help_text="Время выполнения в минутах")
    is_popular = models.BooleanField(default=False, verbose_name="Популярная услуга", db_index=True)  # индекс на популярность
    image = models.ImageField(upload_to="services/", blank=True, verbose_name="Изображение")
    
    def __str__(self):
        return f"{self.name} - {self.price} руб."
    
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['name']
        indexes = [
            # Составной индекс для сортировки по цене и популярности
            models.Index(fields=['price', 'is_popular'], name='service_price_popular_idx'),
        ]

class Master(models.Model):
    """Модель мастера барбершопа."""
    name = models.CharField(max_length=150, verbose_name="Имя", db_index=True)  # индекс на имя
    photo = models.ImageField(upload_to="masters/", blank=True, verbose_name="Фотография")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    experience = models.PositiveIntegerField(verbose_name="Стаж работы", help_text="Опыт работы в годах")
    services = models.ManyToManyField(Service, related_name="masters", verbose_name="Услуги")
    is_active = models.BooleanField(default=True, verbose_name="Активен", db_index=True)  # индекс на статус активности
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"
        ordering = ['name']
        indexes = [
            # Составной индекс для фильтрации по опыту и активности
            models.Index(fields=['experience', 'is_active'], name='master_exp_active_idx'),
        ]

class Order(models.Model):
    """Модель заказа в барбершопе."""
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default="not_approved", 
        verbose_name="Статус",
        db_index=True  # добавляем индекс на поле status
    )
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)  # индекс на дату создания
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    master = models.ForeignKey(
        Master, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Мастер"
    )
    services = models.ManyToManyField(Service, related_name="orders", verbose_name="Услуги")
    appointment_date = models.DateTimeField(verbose_name="Дата и время записи")

    # Поле для отслеживания отправки уведомлений
    notification_sent = models.BooleanField(default=False, verbose_name="Уведомление отправлено")
    
    def __str__(self):
        return f"Заказ {self.id} - {self.client_name} ({self.status})"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date_created']
        indexes = [
            # Составной индекс для полей, часто используемых в поиске и фильтрации
            models.Index(fields=['status', 'appointment_date'], name='order_status_appt_idx'),
        ]

class Review(models.Model):
    """Модель отзыва о мастере."""
    RATING_CHOICES = [
        (1, "1 - Ужасно"),
        (2, "2 - Плохо"),
        (3, "3 - Нормально"),
        (4, "4 - Хорошо"),
        (5, "5 - Отлично"),
    ]
    
    text = models.TextField(verbose_name="Текст отзыва")
    client_name = models.CharField(max_length=100, blank=True, verbose_name="Имя клиента")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name="Мастер")
    photo = models.ImageField(upload_to="reviews/", blank=True, null=True, verbose_name="Фотография")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    
    def __str__(self):
        return f"Отзыв от {self.client_name} о мастере {self.master.name}"
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
