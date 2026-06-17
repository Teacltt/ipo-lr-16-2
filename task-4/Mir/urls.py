from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from Mir import views

router = DefaultRouter() #инициализируем стандартный маршрутизатор для построения адресов api
router.register(r'api/categories', views.CategoryViewSet) #регистрируем конечную точку api для категорий
router.register(r'api/manufacturers', views.ManufacturerViewSet) #регистрируем конечную точку api для производителей
router.register(r'api/products', views.ProductViewSet) #регистрируем конечную точку api для товарных позиций
router.register(r'api/carts', views.CartViewSet) #регистрируем конечную точку api для корзин покупателей
router.register(r'api/cart-items', views.CartItemViewSet) #регистрируем конечную точку api для элементов корзин

urlpatterns = [
    path('admin/', admin.site.urls), #маршрут встроенной панели администратора django
    
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
    
    path('', include(router.urls)), #интегрируем автоматически сгенерированные маршруты api в общий список адресов
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #обслуживание медиа файлов в режиме локальной разработки