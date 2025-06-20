from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.LandingPageView.as_view(), name='landing'),
    path('services/', views.ServicesListView.as_view(), name='services'),
    path('thanks/', views.ThanksView.as_view(), name='thanks'),
    
    # Заказы
    path('orders/', views.OrdersListView.as_view(), name='orders_list'),
    path('orders/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # API для мастеров
    path('api/masters/<int:master_id>/', views.MasterDetailApiView.as_view(), name='master_detail_api'),
    path('booking/', views.BookingView.as_view(), name='booking'),
    path('api/masters/<int:master_id>/services/', views.MasterServicesAjaxView.as_view(), name='master_services_api'),
    
    # Services
    path('services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    
    # Отзывы
    path('reviews/create/', views.ReviewCreateView.as_view(), name='create_review'),
    path('reviews/thanks/', views.ReviewThanksView.as_view(), name='review_thanks'),
    path('api/master-info/', views.MasterInfoAjaxView.as_view(), name='get_master_info'),

    # API автозаполнения
    path('api/autocomplete/client-name/', views.ClientNameAutocompleteView.as_view(), name='client_name_autocomplete'),
    path('api/autocomplete/phone/', views.PhoneAutocompleteView.as_view(), name='phone_autocomplete'),
    path('api/autocomplete/comment/', views.CommentAutocompleteView.as_view(), name='comment_autocomplete'),
]