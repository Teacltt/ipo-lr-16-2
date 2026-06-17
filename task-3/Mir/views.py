from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Category, Manufacturer, Product, Cart, CartItem


def get_or_create_test_cart():
    user, _ = User.objects.get_or_create(username='test_user_asya') #находим или регистрируем тестового пользователя детского мира
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем личную корзину пользователя по второму заданию
    return cart


def detmir_home(request):
    error_message = None #инициализируем пустую переменную для ошибок на главной странице
    success_message = None #инициализируем пустую переменную для успешных уведомлений на главной
    action = request.POST.get('action') #получаем тип действия из отправленной формы

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
    manufacturers = Manufacturer.objects.all() #получаем производителей игрушек из базы данных
    products = Product.objects.all() #получаем все детские товары из базы данных
    carts = Cart.objects.all() #получаем все корзины из базы данных
    
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': error_message,
        'success_message': success_message
    })


def product_list(request):
    products = Product.objects.all() #получаем базовый набор всех детских товаров из базы данных
    query = request.GET.get('q') #получаем строку поиска детского товара от пользователя из запроса
    category_id = request.GET.get('category') #получаем фильтр по категории детских товаров из запроса
    manufacturer_id = request.GET.get('manufacturer') #получаем фильтр по производителю игрушек из запроса

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query)) #выполняем поиск через Q-объекты по заданию

    if category_id:
        products = products.filter(category_id=category_id) #выполняем фильтрацию по детским категориям по заданию

    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id) #выполняем фильтрацию по производителям игрушек по заданию

    categories = Category.objects.all() #получаем все категории детских товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем всех производителей детских товаров из базы данных
    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers
    }) #открываем страницу списка товаров каталога в папке shop по заданию третьего пункта


def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk) #отображение информации о детском работе с обработкой ошибки 404 по заданию
    return render(request, 'shop/product_detail.html', {'product': product}) #открываем страницу детальной информации о детском товаре в папке shop по заданию третьего пункта


def add_to_cart(request, product_id):
    cart = get_or_create_test_cart() #получаем личную корзину текущего покупателя детского мира
    product = get_object_or_404(Product, id=product_id) #находим покупаемую игрушку или возвращаем ошибку 404 по заданию
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0}) #находим элемент
    
    try:
        cart_item.quantity += 1 #увеличиваем количество детского товара в корзине на одну штуку
        cart_item.full_clean() #проверяем валидность данных в модели элемента корзины
        cart_item.save() #сохраняем изменения элемента корзины в базу данных
    except ValidationError:
        pass
    return redirect('cart_view') #перенаправляем пользователя на просмотр корзины покупателя


def update_cart(request, item_id):
    error_message = None #инициализируем пустую переменную для сообщения об ошибке детской корзины
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1)) #получаем новое количество товара из формы
        cart_item = get_object_or_404(CartItem, id=item_id) #находим элемент корзины или возвращаем ошибку 404 по заданию
        try:
            cart_item.quantity = quantity #обновляем поле количества в модели по заданию
            cart_item.full_clean() #запускаем валидацию количества против остатка на складе по заданию
            cart_item.save() #сохраняем обновленный элемент корзины в базу данных
            return redirect('cart_view') #перенаправляем обратно на просмотр корзины детского мира
        except ValidationError as e:
            if 'quantity' in e.message_dict:
                error_message = e.message_dict['quantity'] #перехватываем точный текст ошибки остатков из модели по заданию
            else:
                error_message = "Ошибка валидации количества!" #записываем общую ошибку валидации количества

    cart = get_or_create_test_cart() #получаем текущую корзину детского мира со всеми элементами
    return render(request, 'shop/cart.html', {'cart': cart, 'error_message': error_message}) #открываем страницу корзины в папке shop с ошибкой по заданию третьего пункта


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id) #находим элемент детской корзины по его уникальному номеру id по заданию
    cart_item.delete() #выполняем удаление объекта из базы данных по заданию
    return redirect('cart_view') #перенаправляем пользователя обратно на просмотр корзины детского мира


def cart_view(request):
    cart = get_or_create_test_cart() #получаем корзину со всеми элементами для отображения по заданию
    return render(request, 'shop/cart.html', {'cart': cart}) #отображение всех элементов корзины с общей стоимостью в папке shop по заданию третьего пункта


def about(request):
    return render(request, 'about.html') #открываем страницу информации об авторе детского мира


def info(request):
    return render(request, 'info.html') #открываем страницу общей информации о магазине детских товаров