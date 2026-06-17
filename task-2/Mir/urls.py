from django.urls import path
from . import views

urlpatterns = [
    path('', views.detmir_home, name='home'), #главная витрина детского магазина
    path('about/', views.about, name='about'), #страница об авторе проекта
    path('info/', views.info, name='info'), #страница о магазине детских товаров
    
    path('catalog/', views.product_list, name='product_list'), #новое имя функции каталога по твоему техническому заданию
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #страница детальной карточки детского товара по id
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #новое имя добавления в корзину по техническому заданию
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'), #новое имя обновления количества по техническому заданию
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), #новое имя удаления из корзины по техническому заданию
    path('cart/', views.cart_view, name='cart_view'), #просмотр корзины покупателя детского мира
]