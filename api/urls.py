from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products),
    path('behavior/', views.log_behavior),
    path('recommend/<int:user_id>/', views.get_recommendations),
    path('users/', views.users_list),
]
