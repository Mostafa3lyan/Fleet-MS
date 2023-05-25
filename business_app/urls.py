from django.urls import path
from . import views

urlpatterns = [
    
    path('add_item', views.add_item, name='add_item'),
    path('get_item/<str:item_id>/', views.get_item, name='get_item'),
    path('edit_item/<str:item_id>/', views.edit_item, name='edit_item'),
    path('delete_item/<str:menu_id>/<str:item_id>/', views.delete_item, name='delete_item'),
    path('confirm_order/<str:order_id>/', views.confirm_order, name='confirm_order'),
    path('cancel_order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('get_order_details/<str:order_id>/', views.get_order_details, name='get_order_details'),
    path('view_orders_history/<str:business_id>/', views.view_orders_history, name='view_orders_history'),
    path('view_business_reviews/<str:business_id>/', views.view_business_reviews, name='view_business_reviews'),
    path('add_comment_to_review', views.add_comment_to_review, name='add_comment_to_review'),
    
    
]
