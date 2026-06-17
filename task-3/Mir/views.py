import io
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required #импортируем декоратор ограничения доступа по заданию
from django.core.mail import EmailMessage #импортируем класс для отправки писем с вложениями по заданию
from rest_framework import viewsets
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem
from .serializers import CategorySerializer, ManufacturerSerializer, ProductSerializer, CartSerializer, CartItemSerializer


def get_or_create_test_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем личную корзину конкретного авторизованного пользователя детского мира
    return cart


def detmir_home(request):
    error_message = None #инициализируем пустую переменную для ошибок на главной странице витрины
    success_message = None #инициализируем пустую переменную для успешных уведомлений на главной витрине
    action = request.POST.get('action') #получаем тип действия из отправленной формы витрины

    if request.method == 'POST':
        try:
            if action == 'add_category':
                name = request.POST.get('cat_name')
                desc = request.POST.get('cat_desc')
                category = Category(name=name, description=desc)
                category.full_clean()
                category.save()
                success_message = f"Категория '{name}' успешно создана!"

            elif action == 'add_manufacturer':
                name = request.POST.get('man_name')
                country = request.POST.get('man_country')
                desc = request.POST.get('man_desc')
                manufacturer = Manufacturer(name=name, country=country, description=desc)
                manufacturer.full_clean()
                manufacturer.save()
                success_message = f"Производитель '{name}' успешно создан!"

            elif action == 'add_product':
                name = request.POST.get('prod_name')
                desc = request.POST.get('prod_desc')
                price = request.POST.get('prod_price')
                stock = request.POST.get('prod_stock')
                cat_id = request.POST.get('prod_category')
                man_id = request.POST.get('prod_manufacturer')

                price_val = float(price) if price else 0.0
                stock_val = int(stock) if stock else 0

                product = Product(
                    name=name, description=desc, price=price_val, stock=stock_val,
                    category_id=cat_id, manufacturer_id=man_id
                )
                product.full_clean()
                product.save()
                success_message = f"Товар '{name}' успешно создан!"
                
        except ValidationError as e:
            if 'price' in e.message_dict:
                error_message = e.message_dict['price']
            elif 'stock' in e.message_dict:
                error_message = e.message_dict['stock']
            else:
                error_message = "Ошибка валидации данных!"
        except ValueError:
            error_message = "Введите корректные числовые значения!"

    categories = Category.objects.all() #получаем категории детских товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем производителей товаров для выпадающих списков
    products = Product.objects.all() #получаем все товары витрины из базы данных
    carts = Cart.objects.all() #получаем все корзины пользователей из базы данных
    
    return render(request, 'shop/index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': error_message,
        'success_message': success_message
    }) #открываем обновленную главную страницу детского магазина в папке shop


def product_list(request):
    products = Product.objects.all() #получаем базовый набор всех детских товаров из базы данных
    query = request.GET.get('q') #получаем строку поиска детского товара от пользователя из запроса
    category_id = request.GET.get('category') #получаем фильтр по категории детских товаров из запроса
    manufacturer_id = request.GET.get('manufacturer') #получаем фильтр по производителю бренда из запроса

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query)) #выполняем поиск через Q-объекты

    if category_id:
        products = products.filter(category_id=category_id) #выполняем фильтрацию по детским категориям

    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id) #выполняем фильтрацию по производителям брендам

    categories = Category.objects.all() #получаем все категории детских товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем всех производителей детских товаров из базы данных
    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers
    }) #открываем страницу списка товаров каталога детского магазина в папке shop
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk) #отображение информации о детском работе с обработкой ошибки 404 по заданию
    return render(request, 'shop/product_detail.html', {'product': product}) #открываем страницу детальной информации о детском товаре в папке shop


@login_required #ограничиваем доступ к добавлению в корзину только для авторизованных пользователей по заданию
def add_to_cart(request, product_id):
    cart = get_or_create_test_cart(request.user) #получаем личную корзину текущего вошедшего пользователя детского магазина
    product = get_object_or_404(Product, id=product_id) #находим покупаемый товар или возвращаем ошибку 404
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0}) #находим элемент
    
    try:
        cart_item.quantity += 1 #увеличиваем количество товара в корзине на одну штуку
        cart_item.full_clean() #проверяем валидность данных в модели элемента корзины
        cart_item.save() #сохраняем изменения элемента корзины в базу данных
    except ValidationError:
        pass
    return redirect('cart_view') #перенаправляем пользователя на просмотр корзины покупателя


@login_required #ограничиваем доступ к изменению количества только для авторизованных пользователей по заданию
def update_cart(request, item_id):
    error_message = None #инициализируем пустую переменную для сообщения об ошибке корзины
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1)) #получаем новое количество товара из формы
        cart_item = get_object_or_404(CartItem, id=item_id) #находим элемент корзины или возвращаем ошибку 404
        try:
            cart_item.quantity = quantity #обновляем поле количества в модели
            cart_item.full_clean() #запускаем валидацию количества против остатка товара на складе магазина
            cart_item.save() #сохраняем обновленный элемент корзины в базу данных
            return redirect('cart_view') #перенаправляем обратно на просмотр корзины товаров
        except ValidationError as e:
            if 'quantity' in e.message_dict:
                error_message = e.message_dict['quantity'] #перехватываем точный текст ошибки остатков со склада магазина
            else:
                error_message = "Ошибка валидации количества!" #записываем общую ошибку валидации количества

    cart = get_or_create_test_cart(request.user) #получаем текущую корзину со всеми элементами
    return render(request, 'shop/cart.html', {'cart': cart, 'error_message': error_message}) #открываем страницу корзины в папке shop с ошибкой


@login_required #ограничиваем доступ к удалению из корзины только для авторизованных пользователей по заданию
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id) #находим элемент корзины по его уникальному номеру id
    cart_item.delete() #выполняем удаление объекта элемента из базы данных по заданию
    return redirect('cart_view') #перенаправляем пользователя обратно на просмотр корзины


@login_required #ограничиваем доступ к просмотру корзины только для авторизованных пользователей по заданию
def cart_view(request):
    cart = get_or_create_test_cart(request.user) #получаем корзину со всеми элементами для отображения по заданию
    return render(request, 'shop/cart.html', {'cart': cart}) #отображение всех элементов корзины с общей стоимостью в папке shop


def about(request):
    return render(request, 'about.html') #открываем страницу информации об авторе проекта


def info(request):
    return render(request, 'info.html') #открываем страницу общей информации о магазине детских товаров


@login_required #ограничиваем доступ к оформлению заказа только для авторизованных пользователей
def checkout_view(request):
    cart = get_or_create_test_cart(request.user) #получаем корзину текущего пользователя для оформления заказа
    cart_items = cart.items.all() #считываем содержимое корзины для переноса в заказ

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_cost=cart.total_cost) #создаем запись нового заказа в базе данных
        
        wb = openpyxl.Workbook() #инициализируем генерацию товарного чека в формате Excel
        ws = wb.active #активируем рабочий лист электронной таблицы для записи данных
        ws.title = "Чек заказа" #задаем имя вкладки для создаваемого Excel файла
        
        ws.append(["Чек по заказу №", order.id]) #записываем уникальный номер чека в файл Excel
        ws.append(["Покупатель:", request.user.username]) #записываем имя текущего клиента в файл Excel
        ws.append([]) #вставляем пустую строку для соблюдения структуры документа в таблице
        ws.append(["Товар", "Цена (BYN)", "Количество", "Стоимость"]) #задаем заголовки колонок чека в Excel
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order, product=item.product, price=item.product.price, quantity=item.quantity
            ) #переносим каждую позицию товара из корзины в состав оформленного заказа
            ws.append([item.product.name, item.product.price, item.quantity, item.element_cost]) #добавляем строку с данными товара в Excel
            
        ws.append([]) #вставляем пустую строку перед выводом итоговых данных
        ws.append(["ИТОГО К ОПЛАТЕ:", "", "", order.total_cost]) #записываем финальную сумму к оплате в Excel
        
        wb.save(f"receipt_order_{order.id}.xlsx") #физически сохраняем адекватный читаемый файл Excel на компьютер для проверки
        
        excel_file = io.BytesIO() #создаем байтовый поток в оперативной памяти для виртуального файла
        wb.save(excel_file) #сохраняем сгенерированную Excel таблицу в созданный байтовый поток
        excel_file.seek(0) #сбрасываем указатель потока в начало для последующего чтения данных
        
        user_email = request.user.email if request.user.email else "customer@detmir.by" #определяем электронный адрес покупателя детских товаров
        email = EmailMessage(
            f"Ваш чек по заказу №{order.id} — Детский Мир",
            "Благодарим за покупку в магазине Детский Мир! Ваш чек во вложении.",
            "noreply@detmir.by", [user_email]
        ) #формируем отправку уведомления по электронной почте покупателю
        
        email.attach(f"receipt_order_{order.id}.xlsx", excel_file.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") #прикрепляем сгенерированный Excel файл к письму
        try:
            email.send(fail_silently=True) #отправляем сформированное письмо с вложенным файлом покупателю
        except Exception:
            pass #игнорируем ошибки отправки если локальный почтовый сервер не настроен
            
        cart.items.all().delete() #выполняем полную очистку содержимого корзины после успешного заказа
        return render(request, 'shop/checkout.html', {'order': order, 'success': True}) #открываем страницу успешного оформления заказа

    return render(request, 'shop/checkout.html', {'cart': cart}) #отображаем страницу подтверждения заказа со списком товаров


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all() #считываем полный набор категорий из базы данных для обработки в api
    serializer_class = CategorySerializer #задаем сериализатор для корректного преобразования данных


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all() #считываем полный набор производителей из базы данных для обработки в api
    serializer_class = ManufacturerSerializer #задаем сериализатор для корректного преобразования данных


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all() #считываем полный набор товарных позиций из базы данных для обработки в api
    serializer_class = ProductSerializer #задаем сериализатор для корректного преобразования данных


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all() #считываем полный набор корзин пользователей из базы данных для обработки в api
    serializer_class = CartSerializer #задаем сериализатор для корректного преобразования данных


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all() #считываем полный набор элементов корзин из базы данных для обработки в api
    serializer_class = CartItemSerializer #задаем сериализатор для корректного преобразования данных