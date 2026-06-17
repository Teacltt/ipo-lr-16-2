import io
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from rest_framework import viewsets, generics, permissions as drf_permissions
from rest_framework.response import Response
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile
from .serializers import (
    CategorySerializer, ManufacturerSerializer, ProductSerializer, 
    CartSerializer, CartItemSerializer, ProfileSerializer, OrderSerializer
)
from django.core.paginator import Paginator

def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

def detmir_home(request):
    error_message = None
    success_message = None
    action = request.POST.get('action')
    if request.method == 'POST':
        if action in ['add_category', 'add_manufacturer', 'add_product']:
            if not request.user.is_authenticated or request.user.profile.role not in ['MANAGER', 'ADMIN']:
                raise PermissionDenied("Отказ в доступе.")
        try:
            if action == 'add_category':
                Category.objects.create(name=request.POST.get('cat_name'), description=request.POST.get('cat_desc'))
            elif action == 'add_manufacturer':
                Manufacturer.objects.create(name=request.POST.get('man_name'), country=request.POST.get('man_country'))
            elif action == 'add_product':
                Product.objects.create(
                    name=request.POST.get('prod_name'), description=request.POST.get('prod_desc'),
                    price=float(request.POST.get('prod_price') or 0.0), stock=int(request.POST.get('prod_stock') or 0),
                    category_id=request.POST.get('prod_category'), manufacturer_id=request.POST.get('prod_manufacturer')
                )
            success_message = "Данные успешно сохранены!"
        except Exception:
            error_message = "Ошибка при сохранении!"
    return render(request, 'shop/index.html', {'categories': Category.objects.all(), 'manufacturers': Manufacturer.objects.all(), 'products': Product.objects.all(), 'error_message': error_message, 'success_message': success_message})

def product_list(request):
    products = Product.objects.all().order_by('id')
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'shop/product_list.html', {'page_obj': page_obj, 'categories': Category.objects.all(), 'manufacturers': Manufacturer.objects.all()})

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request.user)
    cart_item, _ = CartItem.objects.get_or_create(cart=cart, product_id=product_id, defaults={'quantity': 0})
    cart_item.quantity += 1; cart_item.save()
    return redirect('product_list')

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id)
        item.quantity = int(request.POST.get('quantity', 1)); item.save()
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id).delete()
    return redirect('cart_view')

@login_required
def cart_view(request):
    return render(request, 'shop/cart.html', {'cart': get_or_create_cart(request.user)})

@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_cost=cart.total_cost)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
        cart.items.all().delete()
        return render(request, 'shop/index.html', {'success_message': f"Заказ №{order.id} успешно оформлен!"})
    return render(request, 'shop/checkout.html', {'cart': cart})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(); p = user.profile
            p.full_name = request.POST.get('full_name', ''); p.phone = request.POST.get('phone', ''); p.address = request.POST.get('address', ''); p.role = 'CUSTOMER'; p.save()
            login(request, user); return redirect('home')
    return render(request, 'shop/register.html', {'form': UserCreationForm()})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user()); return redirect('home')
    return render(request, 'shop/login.html', {'form': AuthenticationForm()})

def logout_view(request):
    logout(request); request.session.flush()
    res = redirect('home'); res.delete_cookie('sessionid'); return res
class UserProfileView(generics.RetrieveUpdateAPIView):
    # Эндпоинт личного профиля покупателя (Задание 3, пункты 1 и 2)
    serializer_class = ProfileSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class OrderViewSet(viewsets.ModelViewSet):
    # Эндпоинт истории заказов с ролевым разграничением выборки (Задание 3, пункт 4)
    serializer_class = OrderSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Менеджер склада и администратор видят все заказы, покупатель — только собственные
        if getattr(user.profile, 'role', '') in ['MANAGER', 'ADMIN']:
            return Order.objects.all()
        return Order.objects.filter(user=user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    # Защита каталога детских товаров (Задание 3, пункт 3)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    class DjangoIsAdminOrReadOnly(drf_permissions.BasePermission):
        def has_permission(self, request, view):
            if request.method in drf_permissions.SAFE_METHODS:
                return True
            # Создание и редактирование игрушек разрешено исключительно роли ADMIN
            return (
                request.user and 
                request.user.is_authenticated and 
                getattr(request.user.profile, 'role', '') == 'ADMIN'
            )
            
    permission_classes = [DjangoIsAdminOrReadOnly]

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

def profile_page_view(request):
    # Визуальная страница личного кабинета покупателя (Задание 4)
    # Обработка анонимных гостей по ТЗ полностью перенесена на фронтенд (в JS)
    return render(request, 'shop/profile.html')