from django.urls import path
from . import views
from . import businessViews
from . import customerViews
from . import driverViews

urlpatterns = [
    
    #business_Views
    path('add_business',businessViews.add_business, name='add_business'),
    path('getAllBusiness',businessViews.getAllBusiness, name='getAllBusiness'),
    path('get_business/<str:business_id>/',businessViews.get_business, name='get_business'),
    path('update_business/<str:business_id>/',businessViews.update_business, name='update_business'),
    path('delete_business/<str:business_id>/',businessViews.delete_business, name='delete_business'),
    path('get_all_business_orders/<str:business_id>/',businessViews.get_all_business_orders, name='get_all_business_orders'),
    path('get_all_orders',businessViews.get_all_orders, name='get_all_orders'),
    path('view_business_reviews',businessViews.view_business_reviews, name='view_business_reviews'),
    
    #customer_Views
    path('get_all_customers',customerViews.get_all_customers, name='get_all_customers'),
    path('getCustomer/<str:customer_id>/',customerViews.getCustomer, name='getCustomer'),
    path('updateCustomer/<str:customer_id>/',customerViews.updateCustomer, name='updateCustomer'),
    path('deleteCustomer/<str:customer_id>/',customerViews.deleteCustomer, name='deleteCustomer'),
    
    #driver_Views
    path('approve_driver',driverViews.approve_driver, name='approve_driver'),
    path('get_vehicle_details/<str:driver_id>/',driverViews.get_vehicle_details, name='get_vehicle_details'), 
    path('getAllDrivers',driverViews.getAllDrivers, name='getAllDrivers'),
    path('view_driver_details/<str:driver_id>/',driverViews.view_driver_details, name='view_driver_details'), 
    path('updateDriver/<str:driver_id>/',driverViews.updateDriver, name='updateDriver'),
    path('deleteDriver/<str:driver_id>/',driverViews.deleteDriver, name='deleteDriver'), 
    
    
    #views
    path('login', views.login, name='login'),
    # path('createCustomer', views.createCustomer, name='createCustomer'),
    path('create_new_account', views.create_new_account, name='create_new_account'),
    path('send_verification_email/<str:user>/', views.send_verification_email, name='send_verification_email'),
    path('verify_account/<str:uidb64>/<str:token>/', views.verify_account, name='verify_account'),
    
    path('change_password', views.change_password, name='change_password'),
    path('edit_account/<str:user_id>/', views.edit_account, name='edit_account'),
    path('delete_account/<str:user_id>/',views.delete_account, name='delete_account'),
     
     
     
     

    
]