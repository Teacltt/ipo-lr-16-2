from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Mir import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='categories')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturers')
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'carts', views.CartViewSet, basename='carts')
router.register(r'cart-items', views.CartItemViewSet, basename='cart-items')
router.register(r'orders', views.OrderViewSet, basename='orders')

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
    
    # ВОТ ЭТОТ МАРШРУТ ОПРЕДЕЛЯЕТ СТРАНИЦУ ЛИЧНОГО КАБИНЕТА (ИСПРАВЛЕНИЕ ОШИБКИ 404):
    path('profile/', views.profile_page_view, name='profile_page'),
    
    # REST API эндпоинт профиля текущей сессии
    path('api/me/', views.UserProfileView.as_view(), name='user-profile-api'),
    
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)