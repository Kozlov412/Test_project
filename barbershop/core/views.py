from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, F
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Service, Master, Order, Review
import datetime
from decimal import Decimal, InvalidOperation
from .forms import ReviewForm


# Базовый миксин для проверки прав персонала
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Миксин для ограничения доступа только для персонала"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к этой странице.")
        return redirect('landing')


# Представления для отображения страниц
class LandingPageView(TemplateView):
    """Классовое представление для главной страницы (лендинга)"""
    template_name = 'core/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Настраиваем минимальную дату для формы (сегодня)
        today = datetime.date.today()
        min_date = today.strftime('%Y-%m-%d')
        
        # Получаем данные из базы
        context['min_date'] = min_date
        context['services'] = Service.objects.all()
        context['masters'] = Master.objects.filter(is_active=True)
        context['orders'] = Order.objects.order_by('-date_created')[:3]  # Последние 3 заказа
        context['reviews'] = Review.objects.filter(is_published=True).order_by('-created_at')[:6]
        
        return context


class ThanksView(TemplateView):
    """Классовое представление для страницы благодарности после заявки"""
    template_name = 'core/thanks.html'
    
    def post(self, request, *args, **kwargs):
        # Для POST-запросов делаем то же самое, что и для GET
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Проверяем наличие source в параметрах запроса или POST-данных
        source = self.kwargs.get('source', '')
        if not source:
            # Проверяем как в GET так и в POST параметрах
            source = self.request.GET.get('source', self.request.POST.get('source', ''))
        
        if source == 'order':
            context['message'] = 'Спасибо за ваш заказ! Мы свяжемся с вами в ближайшее время.'
        elif source == 'review':
            context['message'] = 'Спасибо за ваш отзыв! После модерации он появится на сайте.'
        else:
            context['message'] = 'Спасибо за обращение!'
            
        return context


class ReviewThanksView(TemplateView):
    """Классовое представление страницы благодарности после отзыва"""
    template_name = 'core/review_thanks.html'


# Представления для работы со списками и деталями объектов
class OrdersListView(LoginRequiredMixin, ListView):
    """Классовое представление для списка всех заявок с улучшенным поиском"""
    model = Order
    template_name = 'core/orders_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        # Получаем параметры поиска из GET-запроса
        search_query = self.request.GET.get('query', '')
        search_name = self.request.GET.get('name') == 'on'
        search_phone = self.request.GET.get('phone') == 'on'
        search_comment = self.request.GET.get('comment') == 'on'
        
        # По умолчанию ищем по имени, если ничего не выбрано
        if not any([search_name, search_phone, search_comment]) and search_query:
            search_name = True
        
        # Начинаем с полного QuerySet
        queryset = Order.objects.all()
        
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
                queryset = queryset.filter(q_filters)
        
        # Итоговая сортировка
        return queryset.order_by('-date_created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Параметры поиска для формы
        context['search_query'] = self.request.GET.get('query', '')
        context['search_name'] = self.request.GET.get('name') == 'on'
        context['search_phone'] = self.request.GET.get('phone') == 'on'
        context['search_comment'] = self.request.GET.get('comment') == 'on'
        
        # Подсчёт заказов по статусам для вкладок
        context['statuses'] = {
            'not_approved': Order.objects.filter(status='not_approved').count(),
            'approved': Order.objects.filter(status='approved').count(),
            'in_progress': Order.objects.filter(status='in_progress').count(),
            'completed': Order.objects.filter(status='completed').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
        }
        
        # Данные для автодополнения
        context['unique_names'] = list(Order.objects.values_list('client_name', flat=True).distinct()[:50])
        context['unique_phones'] = list(Order.objects.values_list('phone', flat=True).distinct()[:50])
        context['unique_comments'] = list(Order.objects.exclude(
            Q(comment='') | Q(comment__isnull=True)
        ).values_list('comment', flat=True).distinct()[:50])
        
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Классовое представление для деталей конкретной заявки"""
    model = Order
    template_name = 'core/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'


class ServicesListView(ListView):
    """Классовое представление для страницы услуг"""
    model = Service
    template_name = 'core/services.html'
    context_object_name = 'services'


class BookingView(TemplateView):
    """Классовое представление для страницы записи к мастеру"""
    template_name = 'core/booking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получить ID мастера, если он передан в GET-параметрах
        master_id = self.request.GET.get('master_id')
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
        
        context.update({
            'master': master,
            'master_services': master_services,
            'all_services': all_services,
            'all_masters': all_masters,
            'min_date': min_date,
        })
        
        return context


# Представления для работы с формами
class ServiceCreateView(LoginRequiredMixin, View):
    """Классовое представление для создания новой услуги"""
    template_name = 'core/service_create.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form_data': {}})
    
    def post(self, request, *args, **kwargs):
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
            return render(request, self.template_name, {
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
            return render(request, self.template_name, {
                'success_message': success_message,
                'form_data': {}  # Очищаем форму
            })
            
        except Exception as e:
            error_message = f"Произошла ошибка при сохранении услуги: {str(e)}"
            return render(request, self.template_name, {
                'error_message': error_message,
                'form_data': form_data
            })


class MasterEditView(LoginRequiredMixin, View):
    """Классовое представление для создания/редактирования мастера"""
    template_name = 'core/master_edit.html'
    
    def get(self, request, *args, **kwargs):
        master_id = kwargs.get('master_id')
        
        # Для редактирования существующего мастера
        if master_id:
            master = get_object_or_404(Master, id=master_id)
        else:
            # Для создания нового мастера
            master = Master()
        
        # Получаем все услуги для формы
        services = Service.objects.all()
        
        return render(request, self.template_name, {
            'master': master,
            'services': services,
            'form_data': {}
        })
    
    def post(self, request, *args, **kwargs):
        master_id = kwargs.get('master_id')
        
        # Для редактирования существующего мастера
        if master_id:
            master = get_object_or_404(Master, id=master_id)
        else:
            # Для создания нового мастера
            master = Master()
        
        # Получаем все услуги для формы
        services = Service.objects.all()
        
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
            return render(request, self.template_name, {
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
            return render(request, self.template_name, {
                'success_message': success_message,
                'master': master,
                'services': services
            })
            
        except Exception as e:
            error_message = f"Произошла ошибка при сохранении мастера: {str(e)}"
            return render(request, self.template_name, {
                'error_message': error_message,
                'form_data': form_data,
                'master': master,
                'services': services
            })


class ReviewCreateView(CreateView):
    """Классовое представление для создания нового отзыва"""
    model = Review
    form_class = ReviewForm
    template_name = 'core/review_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        # Предзаполняем форму, если передан id мастера
        master_id = self.request.GET.get('master_id')
        if master_id:
            try:
                master = Master.objects.get(id=master_id)
                initial['master'] = master
            except Master.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        # Создаем новый отзыв, но не публикуем его сразу (требуется модерация)
        review = form.save(commit=False)
        review.is_published = False  # Отзыв не публикуется автоматически
        review.save()
        
        # Сохраняем связи многие-ко-многим (если они есть)
        form.save_m2m()
        
        return redirect('review_thanks')


class MasterDetailView(DetailView):
    """Классовое представление для детальной информации о мастере"""
    model = Master
    template_name = 'core/master_detail.html'
    context_object_name = 'master'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        master = self.object
        
        # Добавляем в контекст отзывы и услуги мастера
        context['reviews'] = master.review_set.filter(is_published=True)
        context['services'] = master.services.all()
        
        return context
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        master_id = self.kwargs.get('pk')
        
        # Получаем мастера
        master = get_object_or_404(queryset, pk=master_id)
        
        # Увеличиваем счетчик просмотров атомарно
        Master.objects.filter(pk=master_id).update(view_count=F('view_count') + 1)
        
        # Обновляем объект после изменения счетчика
        master.refresh_from_db()
        
        # Сохраняем информацию о просмотренных мастерах в сессии
        viewed_masters = self.request.session.get('viewed_masters', [])
        if master.pk not in viewed_masters:
            viewed_masters.append(master.pk)
            self.request.session['viewed_masters'] = viewed_masters
            self.request.session.modified = True
        
        return master


# AJAX-представления
class ClientNameAutocompleteView(View):
    """Классовое представление для API автозаполнения имен клиентов"""
    def get(self, request, *args, **kwargs):
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


class PhoneAutocompleteView(View):
    """Классовое представление для API автозаполнения телефонов"""
    def get(self, request, *args, **kwargs):
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


class CommentAutocompleteView(View):
    """Классовое представление для API автозаполнения комментариев"""
    def get(self, request, *args, **kwargs):
        query = request.GET.get('term', '')
        if len(query) < 3:
            return JsonResponse([], safe=False)
            
        comments = Order.objects.filter(
            comment__icontains=query
        ).exclude(comment='').values_list('comment', flat=True).distinct()
        
        results = list(comments)[:10]
        
        return JsonResponse(results, safe=False)


class MasterDetailApiView(View):
    """Классовое представление для API получения данных о мастере"""
    def get(self, request, master_id, *args, **kwargs):
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


class MasterInfoAjaxView(View):
    """Классовое представление для API получения информации о мастере через AJAX"""
    def get(self, request, *args, **kwargs):
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


class MasterServicesAjaxView(View):
    """Классовое представление для API получения услуг мастера"""
    def get(self, request, master_id, *args, **kwargs):
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