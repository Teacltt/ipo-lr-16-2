from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Mir import views

router = DefaultRouter()
router.register(r'api/categories', views.CategoryViewSet)
router.register(r'api/manufacturers', views.ManufacturerViewSet)
router.register(r'api/products', views.ProductViewSet)
router.register(r'api/carts', views.CartViewSet)
router.register(r'api/cart-items', views.CartItemViewSet)
# Параметр basename для бесконфликтной работы динамического ролевого get_queryset (Пункт 4)
router.register(r'api/orders', views.OrderViewSet, basename='orders')
urlpatterns = [
    path('', views.detmir_home, name='home'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Новый REST API эндпоинт профиля пользователя (Задание 3, пункты 1 и 2)
    path('api/me/', views.UserProfileView.as_view(), name='user-profile-api'),
    
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)