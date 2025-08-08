from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('become-vendor/', views.become_vendor, name='become_vendor'),
    path('create-order/', views.create_order, name='create_order'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-status/<str:order_id>/', views.order_status, name='order_status'),
] 