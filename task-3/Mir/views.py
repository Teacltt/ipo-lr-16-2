import random
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem


def get_or_create_test_cart():
    user, _ = User.objects.get_or_create(username='test_user_asya')
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def fill_database():
    countries = ['Беларусь', 'Россия', 'Китай', 'Германия', 'Польша']
    manufacturers = []

    for i in range(1, 6):
        m, _ = Manufacturer.objects.get_or_create(
            name=f"Детский Бренд {i}",
            defaults={'country': random.choice(countries), 'description': 'Описание'}
        )
        manufacturers.append(m) #заполняем производителей по тз

    category_names = [
        'Игрушки', 'Коляски', 'Одежда', 'Подгузники', 'Детское питание',
        'Погремушки', 'Книжки', 'Конструкторы', 'Обувь', 'Канцелярия'
    ]
    categories = []

    for name in category_names:
        c, _ = Category.objects.get_or_create(name=name, defaults={'description': 'Описание'})
        categories.append(c) #заполняем категории по тз

    for i in range(1, 35):
        category = categories[(i - 1) % len(categories)]
        manufacturer = random.choice(manufacturers)
        Product.objects.get_or_create(
            name=f"Детский товар №{i}",
            defaults={
                'description': 'Качественный товар для детей в магазине Детский Мир',
                'price': random.randint(5, 150),
                'stock': random.randint(5, 30),
                'category': category,
                'manufacturer': manufacturer
            }
        ) #заполняем товары по тз

    for i in range(1, 6):
        username = f"user_{i}"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(f"password_{i}")
            user.save()

        cart, _ = Cart.objects.get_or_create(user=user)
        CartItem.objects.filter(cart=cart).delete()
        all_products = list(Product.objects.all())
        random_products = random.sample(all_products, 2)

        for prod in random_products:
            CartItem.objects.create(
                cart=cart,
                product=prod,
                quantity=random.randint(1, 2)
            ) #заполняем пользователей и корзины по тз

    print("Готово")


def detmir(request):
    fill_database() #запускаем автозаполнение по тз
    cart = get_or_create_test_cart()
    
    if request.method == 'POST' and request.POST.get('action') == 'add_to_cart':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
        try:
            cart_item.quantity += quantity
            cart_item.full_clean()
            cart_item.save()
            return redirect('/')
        except ValidationError as e:
            categories = Category.objects.all()
            manufacturers = Manufacturer.objects.all()
            products = Product.objects.all()
            return render(request, 'index.html', {
                'categories': categories, 'manufacturers': manufacturers, 'products': products,
                'cart': cart, 'error_message': e.message_dict.get('quantity', ["Ошибка количества"])
            })

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    products = Product.objects.all()
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'cart': cart
    })


def admin_panel(request):
    error_message = None
    success_message = None
    action = request.POST.get('action')

    if request.method == 'POST':
        try:
            if action == 'add_category':
                name = request.POST.get('cat_name')
                desc = request.POST.get('cat_desc')
                Category.objects.create(name=name, description=desc)
                success_message = f"Категория '{name}' создана!"
            elif action == 'add_manufacturer':
                name = request.POST.get('man_name')
                country = request.POST.get('man_country')
                desc = request.POST.get('man_desc')
                Manufacturer.objects.create(name=name, country=country, description=desc)
                success_message = f"Производитель '{name}' создан!"
            elif action == 'add_product':
                name = request.POST.get('prod_name')
                desc = request.POST.get('prod_desc')
                price = float(request.POST.get('prod_price', 0))
                stock = int(request.POST.get('prod_stock', 0))
                cat_id = request.POST.get('prod_category')
                man_id = request.POST.get('prod_manufacturer')
                
                product = Product(name=name, description=desc, price=price, stock=stock, category_id=cat_id, manufacturer_id=man_id)
                product.full_clean()
                product.save()
                success_message = f"Товар '{name}' создан!"
        except ValidationError as e:
            error_message = str(e)

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    return render(request, 'admin_panel.html', {
        'categories': categories, 'manufacturers': manufacturers,
        'error_message': error_message, 'success_message': success_message
    })


def cart_view(request):
    cart = get_or_create_test_cart()
    return render(request, 'cart.html', {'cart': cart})


def author(request):
    return render(request, 'author.html')


def shop(request):
    return render(request, 'shop.html')