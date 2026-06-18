from django.urls import path #импорт библиотеки
from . import views #импорт библиотеки

urlpatterns = [
    path('', views.detmir, name='home'), #главная витрина
    path('admin_panel/', views.admin_panel, name='admin_panel'), #наша панель управления
    path('cart/', views.cart_view, name='cart_view'), #страница корзины по тз
    path('author/', views.author, name='author'), #страница автора
    path('shop/', views.shop, name='shop'), #страница о магазине
]