from django.urls import path
from . import views

urlpatterns = [
    path('', views.detmir_home, name='home'), #главная страница со всеми списками детского мира
    path('about/', views.about, name='about'), #страница об авторе проекта
    path('info/', views.info, name='info'), #страница о магазине детских товаров
    path('catalog/', views.catalog_view, name='catalog_view'), #страница каталога детских товаров
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #страница детальной карточки товара по его id
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'), #маршрут для добавления детского товара в корзину
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'), #маршрут для обновления количества в корзине
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'), #маршрут для удаления товара из корзины
    path('cart/', views.cart_view, name='cart_view'), #маршрут для просмотра корзины покупателя детского мира
]