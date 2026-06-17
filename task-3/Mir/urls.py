from django.urls import path
from . import views

urlpatterns = [
    path('', views.detmir_home, name='home'), #главная витрина детского магазина со всеми списками
    path('about/', views.about, name='about'), #страница об авторе проекта
    path('info/', views.info, name='info'), #страница о магазине детских товаров
    
    path('catalog/', views.product_list, name='product_list'), #страница каталога детских товаров
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #страница детальной карточки детского товара по id
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #маршрут для добавления товара в корзину магазина
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'), #маршрут для обновления количества товара в корзине
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), #маршрут для удаления товара из корзины детского магазина
    path('cart/', views.cart_view, name='cart_view'), #просмотр корзины покупателя детских товаров
    
    path('checkout/', views.checkout_view, name='checkout_view'), #страница оформления заказа детских товаров
]