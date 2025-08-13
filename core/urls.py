from django.urls import path
from . import views, crm_views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('become-vendor/', views.become_vendor, name='become_vendor'),
    path('create-order/', views.create_order, name='create_order'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-status/<str:order_id>/', views.order_status, name='order_status'),
    
    # CRM URLs for Project Managers
    path('crm/', crm_views.crm_dashboard, name='crm_dashboard'),
    path('crm/orders/', crm_views.crm_orders, name='crm_orders'),
    path('crm/orders/<str:order_id>/', crm_views.crm_order_detail, name='crm_order_detail'),
    path('crm/vendors/', crm_views.crm_vendors, name='crm_vendors'),
    path('crm/vendors/create/', crm_views.crm_vendor_create, name='crm_vendor_create'),
    path('crm/vendors/<int:vendor_id>/', crm_views.crm_vendor_detail, name='crm_vendor_detail'),
    path('crm/vendors/<int:vendor_id>/edit/', crm_views.crm_vendor_edit, name='crm_vendor_edit'),
    path('crm/analytics/', crm_views.crm_analytics, name='crm_analytics'),
    path('crm/update-order-status/', crm_views.crm_update_order_status, name='crm_update_order_status'),
    path('crm/add-order-update/', crm_views.crm_add_order_update, name='crm_add_order_update'),
    path('crm/assign-vendor/', crm_views.crm_assign_vendor, name='crm_assign_vendor'),
    path('crm/update-delivery/', crm_views.crm_update_delivery, name='crm_update_delivery'),
    path('crm/set-expected-date/', crm_views.crm_set_expected_date, name='crm_set_expected_date'),
    path('crm/set-actual-date/', crm_views.crm_set_actual_date, name='crm_set_actual_date'),
] 