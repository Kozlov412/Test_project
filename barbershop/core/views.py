from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Service, Master, Order, Review
from django.http import JsonResponse
import datetime
from decimal import Decimal, InvalidOperation
from .models import Review, Master
from .forms import ReviewForm

def landing(request):
    """
    Представление для главной страницы (лендинга)
    """
    # Настраиваем минимальную дату для формы (сегодня)
    today = datetime.date.today()
    min_date = today.strftime('%Y-%m-%d')
    
    # Получаем данные из базы
    services = Service.objects.all()
    masters = Master.objects.filter(is_active=True)
    # Получаем последние 3 заказа для примера
    recent_orders = Order.objects.order_by('-date_created')[:3]
    # Получаем опубликованные отзывы
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')[:6]
    
    context = {
        'min_date': min_date,
        'services': services,
        'masters': masters,
        'orders': recent_orders,
        'reviews': reviews,
    }

    return render(request, 'core/landing.html', context)

def thanks(request):
    """
    Представление для страницы благодарности после заявки
    """
    return render(request, 'core/thanks.html')

@login_required
def orders_list(request):
    """
    Представление для списка всех заявок с улучшенным поиском
    """
    # Получаем параметры поиска из GET-запроса
    search_query = request.GET.get('query', '')
    search_name = request.GET.get('name') == 'on'
    search_phone = request.GET.get('phone') == 'on'
    search_comment = request.GET.get('comment') == 'on'
    
    # По умолчанию ищем по имени, если ничего не выбрано
    if not any([search_name, search_phone, search_comment]) and search_query:
        search_name = True
    
    # Начинаем с полного QuerySet
    orders = Order.objects.all()
    
    # Применяем фильтры поиска, если есть поисковый запрос
    if search_query:
        q_filters = Q()
        
        if search_name:
            # Поиск по имени нечувствительный к регистру
            q_filters |= Q(client_name__icontains=search_query)
        
        if search_phone:
            # Поиск по телефону
            q_filters |= Q(phone__icontains=search_query)
            
        if search_comment:
            # Поиск по комментарию нечувствительный к регистру
            q_filters |= Q(comment__icontains=search_query)
            
        if q_filters:
            orders = orders.filter(q_filters)
    
    # Итоговая сортировка
    orders = orders.order_by('-date_created')
    
    # Подсчёт заказов по статусам для вкладок
    statuses = {
        'not_approved': Order.objects.filter(status='not_approved').count(),
        'approved': Order.objects.filter(status='approved').count(),
        'in_progress': Order.objects.filter(status='in_progress').count(),
        'completed': Order.objects.filter(status='completed').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }
    
    # Получаем уникальные имена, телефоны и комментарии для автодополнения
    # Используем values_list с аргументом flat=True для получения плоского списка
    # Также используем distinct() для исключения дубликатов
    unique_names = list(Order.objects.values_list('client_name', flat=True).distinct()[:50])
    unique_phones = list(Order.objects.values_list('phone', flat=True).distinct()[:50])
    
    # Для комментариев исключаем пустые значения и дубликаты
    unique_comments = list(Order.objects.exclude(
        Q(comment='') | Q(comment__isnull=True)
    ).values_list('comment', flat=True).distinct()[:50])
    
    context = {
        'orders': orders,
        'statuses': statuses,
        'search_query': search_query,
        'search_name': search_name,
        'search_phone': search_phone,
        'search_comment': search_comment,
        # Для автодополнения
        'unique_names': unique_names,
        'unique_phones': unique_phones,
        'unique_comments': unique_comments,
    }
    return render(request, 'core/orders_list.html', context)



@login_required
def order_detail(request, order_id):
    """
    Представление для деталей конкретной заявки
    Доступно только авторизованным пользователям
    """
    # Получаем заказ по ID или выдаем 404
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order
    }
    return render(request, 'core/order_detail.html', context)

@login_required
def client_name_autocomplete(request):
    """API для автозаполнения имен клиентов"""
    query = request.GET.get('term', '')
    if len(query) < 2:  # Не выполняем поиск для коротких запросов
        return JsonResponse([], safe=False)
        
    # Поиск клиентов по имени
    clients = Order.objects.filter(
        client_name__icontains=query
    ).values_list('client_name', flat=True).distinct()
    
    # Максимум 10 результатов
    results = list(clients)[:10]
    
    return JsonResponse(results, safe=False)

@login_required
def phone_autocomplete(request):
    """API для автозаполнения телефонов"""
    query = request.GET.get('term', '')
    if len(query) < 3:  # Не выполняем поиск для коротких запросов
        return JsonResponse([], safe=False)
        
    # Поиск телефонов
    phones = Order.objects.filter(
        phone__icontains=query
    ).values_list('phone', flat=True).distinct()
    
    # Максимум 10 результатов
    results = list(phones)[:10]
    
    return JsonResponse(results, safe=False)

@login_required
def comment_autocomplete(request):
    """API для автозаполнения комментариев"""
    query = request.GET.get('term', '')
    if len(query) < 3:
        return JsonResponse([], safe=False)
        
    comments = Order.objects.filter(
        comment__icontains=query
    ).exclude(comment='').values_list('comment', flat=True).distinct()
    
    results = list(comments)[:10]
    
    return JsonResponse(results, safe=False)

def services_page(request):
    """
    Отдельная страница для услуг
    """
    services = Service.objects.all()
    
    context = {
        'services': services,
    }
    return render(request, 'core/services.html', context)

@login_required  # Ограничим доступ только для авторизованных пользователей
def service_create(request):
    """
    Представление для создания новой услуги
    """
    # Для хранения данных формы в случае ошибок
    form_data = {}
    
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price_str = request.POST.get('price', '').strip()
        duration_str = request.POST.get('duration', '').strip()
        is_popular = request.POST.get('is_popular') == 'on'
        image = request.FILES.get('image')
        
        # Сохраняем данные для повторного отображения формы в случае ошибок
        form_data = {
            'name': name,
            'description': description,
            'price': price_str,
            'duration': duration_str,
            'is_popular': is_popular
        }
        
        # Валидация данных
        errors = []
        
        if not name:
            errors.append("Название услуги обязательно")
        
        try:
            price = Decimal(price_str)
            if price <= 0:
                errors.append("Цена должна быть положительным числом")
        except (InvalidOperation, ValueError):
            errors.append("Некорректный формат цены")
        
        try:
            duration = int(duration_str)
            if duration <= 0:
                errors.append("Длительность должна быть положительным числом")
        except ValueError:
            errors.append("Некорректный формат длительности")
        
        # Если есть ошибки, показываем форму снова с сообщениями об ошибках
        if errors:
            error_message = " ".join(errors)
            return render(request, 'service_create.html', {  # Изменена ссылка на шаблон
                'error_message': error_message,
                'form_data': form_data
            })
        
        # Создаем и сохраняем новую услугу
        try:
            service = Service(
                name=name,
                description=description,
                price=price,
                duration=duration,
                is_popular=is_popular
            )
            
            if image:
                service.image = image
            
            service.save()
            
            # После успешного сохранения показываем сообщение об успехе
            success_message = f"Услуга '{name}' успешно создана!"
            return render(request, 'core\service_create.html', {  # Изменена ссылка на шаблон
                'success_message': success_message,
                'form_data': {}  # Очищаем форму
            })
            
        except Exception as e:
            error_message = f"Произошла ошибка при сохранении услуги: {str(e)}"
            return render(request, 'core\service_create.html', {  # Изменена ссылка на шаблон
                'error_message': error_message,
                'form_data': form_data
            })
    
    # Если метод GET, просто показываем пустую форму
    return render(request, 'core/service_create.html', {'form_data': form_data})  # Изменена ссылка на шаблон

@login_required
def master_edit(request, master_id=None):
    """
    Представление для создания/редактирования мастера
    """
    # Для редактирования существующего мастера
    if master_id:
        master = get_object_or_404(Master, id=master_id)
    else:
        # Для создания нового мастера
        master = Master()
    
    # Получаем все услуги для формы
    services = Service.objects.all()
    
    # Для хранения данных формы в случае ошибок
    form_data = {}
    
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        experience_str = request.POST.get('experience', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        selected_services = request.POST.getlist('services')
        remove_photo = request.POST.get('remove_photo') == 'on'
        photo = request.FILES.get('photo')
        
        # Сохраняем данные для повторного отображения формы в случае ошибок
        form_data = {
            'name': name,
            'phone': phone,
            'address': address,
            'experience': experience_str,
            'is_active': is_active,
            'services': selected_services
        }
        
        # Валидация данных
        errors = []
        
        if not name:
            errors.append("Имя мастера обязательно")
        if not phone:
            errors.append("Телефон обязателен")
        if not address:
            errors.append("Адрес обязателен")
        
        try:
            experience = int(experience_str)
            if experience < 0:
                errors.append("Стаж работы не может быть отрицательным")
        except ValueError:
            errors.append("Некорректный формат стажа работы")
        
        # Если есть ошибки, показываем форму снова с сообщениями об ошибках
        if errors:
            error_message = " ".join(errors)
            return render(request, 'core/master_edit.html', {
                'error_message': error_message,
                'form_data': form_data,
                'master': master,
                'services': services
            })
        
        # Создаем и сохраняем мастера
        try:
            master.name = name
            master.phone = phone
            master.address = address
            master.experience = experience
            master.is_active = is_active
            
            # Обработка фотографии
            if remove_photo and master.photo:
                master.photo.delete()  # Удаляем файл
                master.photo = None
            
            if photo:
                if master.photo:
                    master.photo.delete()  # Удаляем старый файл, если есть
                master.photo = photo
            
            master.save()
            
            # Обновляем связи с услугами
            master.services.clear()
            for service_id in selected_services:
                try:
                    service = Service.objects.get(id=service_id)
                    master.services.add(service)
                except Service.DoesNotExist:
                    pass
            
            # После успешного сохранения показываем сообщение об успехе
            success_message = f"Мастер '{name}' успешно {'обновлен' if master_id else 'создан'}!"
            return render(request, 'core/master_edit.html', {
                'success_message': success_message,
                'master': master,
                'services': services
            })
            
        except Exception as e:
            error_message = f"Произошла ошибка при сохранении мастера: {str(e)}"
            return render(request, 'core/master_edit.html', {
                'error_message': error_message,
                'form_data': form_data,
                'master': master,
                'services': services
            })
    
    # Если метод GET, просто показываем форму
    return render(request, 'core/master_edit.html', {
        'master': master,
        'services': services,
        'form_data': form_data
    })

def create_review(request):
    """
    Представление для создания нового отзыва
    """
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Создаем новый отзыв, но не публикуем его сразу (требуется модерация)
            review = form.save(commit=False)
            review.is_published = False  # Отзыв не публикуется автоматически
            review.save()
            
            # Перенаправляем на страницу благодарности
            return redirect('review_thanks')
    else:
        # Предзаполняем форму, если передан id мастера
        master_id = request.GET.get('master_id')
        if master_id:
            try:
                master = Master.objects.get(id=master_id)
                form = ReviewForm(initial={'master': master})
            except Master.DoesNotExist:
                form = ReviewForm()
        else:
            form = ReviewForm()
    
    return render(request, 'core/review_form.html', {'form': form})

def review_thanks(request):
    """
    Страница благодарности после отправки отзыва
    """
    return render(request, 'core/review_thanks.html')

def get_master_info(request):
    """
    Универсальное представление для получения информации о мастере через AJAX.
    Возвращает данные мастера в формате JSON.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        master_id = request.GET.get('master_id')
        if master_id:
            try:
                master = Master.objects.get(pk=master_id)
                # Формируем данные для ответа
                master_data = {
                    'id': master.id,
                    'name': f"{master.name}",
                    'experience': master.experience,
                    'photo': master.photo.url if master.photo else None,
                    'services': list(master.services.values('id', 'name', 'price')),
                }
                return JsonResponse({'success': True, 'master': master_data})
            except Master.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Мастер не найден'})
        return JsonResponse({'success': False, 'error': 'Не указан ID мастера'})
    return JsonResponse({'success': False, 'error': 'Недопустимый запрос'})

def master_detail_api(request, master_id):
    """API для получения данных о мастере в формате JSON"""
    try:
        master = Master.objects.get(id=master_id)
        data = {
            'id': master.id,
            'name': master.name,
            'experience': master.experience,
            'photo_url': master.photo.url if master.photo else None,
            'services': list(master.services.values_list('name', flat=True)),
        }
        return JsonResponse(data)
    except Master.DoesNotExist:
        return JsonResponse({'error': 'Мастер не найден'}, status=404)
    

def booking(request):
    """Представление для страницы записи к мастеру"""
    # Получить ID мастера, если он передан в GET-параметрах
    master_id = request.GET.get('master_id')
    master = None
    master_services = None
    
    # Если выбран мастер, получим его и его услуги
    if master_id:
        try:
            master = Master.objects.get(id=master_id)
            master_services = master.services.all()
        except Master.DoesNotExist:
            master = None
    
    # Получить все услуги, если мастер не выбран или нужны все услуги
    all_services = Service.objects.all()
    all_masters = Master.objects.filter(is_active=True)
    
    # Настраиваем минимальную дату для формы (сегодня)
    today = datetime.date.today()
    min_date = today.strftime('%Y-%m-%d')
    
    context = {
        'master': master,
        'master_services': master_services,
        'all_services': all_services,
        'all_masters': all_masters,
        'min_date': min_date,
    }
    return render(request, 'core/booking.html', context)

def master_services_api(request, master_id):
    """API для получения услуг мастера в формате JSON"""
    try:
        master = Master.objects.get(id=master_id)
        services = master.services.all()
        services_data = [
            {
                'id': service.id,
                'name': service.name,
                'price': float(service.price),  # Преобразуем Decimal в float для JSON
                'duration': service.duration
            }
            for service in services
        ]
        return JsonResponse({'services': services_data})
    except Master.DoesNotExist:
        return JsonResponse({'error': 'Мастер не найден'}, status=404)
    