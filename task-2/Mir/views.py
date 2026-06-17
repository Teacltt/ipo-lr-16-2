import io
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required # Ограничение доступа к корзине и чекам
from django.core.mail import EmailMessage # Отправка чеков с вложениями Excel
from django.contrib.auth import login, authenticate, logout # Сессионная аутентификация
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Классические формы Django
from django.core.paginator import Paginator # Пагинация каталога игрушек
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem

def get_or_create_cart(user):
    # Инициализация личной корзины покупателя детских товаров
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

def detmir_home(request):
    error_message = None
    success_message = None
    action = request.POST.get('action')
    
    if request.method == 'POST':
        if action in ['add_category', 'add_manufacturer', 'add_product']:
            if not request.user.is_authenticated or request.user.profile.role not in ['MANAGER', 'ADMIN']:
                raise PermissionDenied("У вас нет прав для управления ассортиментом Детского мира.")

        try:
            if action == 'add_category':
                name = request.POST.get('cat_name')
                desc = request.POST.get('cat_desc')
                category = Category(name=name, description=desc)
                category.full_clean()
                category.save()
                success_message = f"Категория '{name}' успешно добавлена!"
                
            elif action == 'add_manufacturer':
                name = request.POST.get('man_name')
                country = request.POST.get('man_country')
                desc = request.POST.get('man_desc')
                manufacturer = Manufacturer(name=name, country=country, description=desc)
                manufacturer.full_clean()
                manufacturer.save()
                success_message = f"Бренд '{name}' успешно добавлен!"
                
            elif action == 'add_product':
                name = request.POST.get('prod_name')
                desc = request.POST.get('prod_desc')
                price = request.POST.get('prod_price')
                stock = request.POST.get('prod_stock')
                cat_id = request.POST.get('prod_category')
                man_id = request.POST.get('prod_manufacturer')
                
                product = Product(
                    name=name, description=desc, price=float(price or 0.0), stock=int(stock or 0),
                    category_id=cat_id, manufacturer_id=man_id
                )
                product.full_clean()
                product.save()
                success_message = f"Товар '{name}' успешно опубликован!"
                
        except ValidationError:
            error_message = "Ошибка валидации спецификаций товара!"
        except ValueError:
            error_message = "Введите корректные числовые показатели!"

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    products = Product.objects.all()
    
    return render(request, 'shop/index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'error_message': error_message,
        'success_message': success_message
    })

def product_list(request):
    products = Product.objects.all().order_by('id')
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
        
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shop/product_list.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all()
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
    if cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('product_list')

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)
        if quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_cost=cart.total_cost)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Заказ {order.id}"
        ws.append([f"Товарный чек по заказу № {order.id} — «Детский мир»"])
        ws.append([f"Покупатель: {request.user.username}"])
        ws.append([])
        ws.append(["Наименование товара", "Цена (BYN)", "Количество", "Стоимость"])

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
            ws.append([item.product.name, item.product.price, item.quantity, item.element_cost])

        ws.append([])
        ws.append(["ИТОГО К ОПЛАТЕ:", "", "", order.total_cost])

        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        email = EmailMessage(
            f"Товарный чек по заказу №{order.id} — Детский Мир",
            "Спасибо за покупку! Ваш чек прикреплен к письму.",
            "noreply@detmir.by",
            [request.user.email if request.user.email else "customer@detmir.by"]
        )
        email.attach(f"receipt_order_{order.id}.xlsx", excel_file.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        try:
            email.send(fail_silently=True)
        except Exception:
            pass

        cart.items.all().delete()
        return render(request, 'shop/index.html', {'success_message': f"Заказ №{order.id} успешно оформлен! Чек отправлен на почту."})

    return render(request, 'shop/checkout.html', {'cart': cart})

def register_view(request):
    # Регистрация нового покупателя торговой площадки (Задание 2)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.full_name = request.POST.get('full_name', '')
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.role = 'CUSTOMER' # По умолчанию обычный Покупатель
            profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    # Аутентификация пользователя с автоматической генерацией куки сессии
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) # Выдача сессионного токена в Cookies
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    # Принудительное уничтожение сессии и стирание cookies из браузера
    logout(request)
    request.session.flush() # Сброс состояния на сервере
    response = redirect('home')
    response.delete_cookie('sessionid') # Удаление сессионной куки клиента
    return response