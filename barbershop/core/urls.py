from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('services/', views.services_page, name='services'),
    path('thanks/', views.thanks, name='thanks'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('api/masters/<int:master_id>/', views.master_detail_api, name='master_detail_api'),
    path('booking/', views.booking, name='booking'),
    path('api/masters/<int:master_id>/services/', views.master_services_api, name='master_services_api'),
    path('services/create/', views.service_create, name='service_create'),
    # Новые маршруты для отзывов
    path('reviews/create/', views.create_review, name='create_review'),
    path('reviews/thanks/', views.review_thanks, name='review_thanks'),
    path('api/master-info/', views.get_master_info, name='get_master_info'),

    # API автозаполнения
    path('api/autocomplete/client-name/', views.client_name_autocomplete, name='client_name_autocomplete'),
    path('api/autocomplete/phone/', views.phone_autocomplete, name='phone_autocomplete'),
    path('api/autocomplete/comment/', views.comment_autocomplete, name='comment_autocomplete'),
]
