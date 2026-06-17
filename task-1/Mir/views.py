from django.shortcuts import render, redirect
from .models import Category, Manufacturer, Product, Cart, CartItem


def get_or_create_test_cart():
    user, _ = User.objects.get_or_create(username='test_user_asya') #находим или регистрируем тестового пользователя детского мира
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем личную корзину пользователя по первому заданию
    return cart


def detmir_home(request):
    categories = Category.objects.all() #получаем категории детских товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем производителей игрушек из базы данных
    products = Product.objects.all() #получаем все детские товары из базы данных
    carts = Cart.objects.all() #получаем все корзины покупателей из базы данных
    
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts
    })


def catalog_view(request):
    products = Product.objects.all() #получаем все детские товары для каталога из базы данных
    return render(request, 'catalog.html', {'products': products}) #открываем страницу каталога детского мира


def product_detail(request, pk):
    product = Product.objects.get(id=pk) #находим один конкретный детский товар по его идентификатору id
    return render(request, 'product_detail.html', {'product': product}) #открываем детальную карточку детского товара


def cart_view(request):
    cart = get_or_create_test_cart() #получаем текущую корзину покупателя детского мира
    return render(request, 'cart.html', {'cart': cart}) #открываем страницу просмотра корзины пользователя


def cart_add(request, product_id):
    cart = get_or_create_test_cart() #получаем текущую корзину покупателя детского мира
    product = Product.objects.get(id=product_id) #находим покупаемый детский товар по его идентификатору
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
    try:
        cart_item.quantity += 1 #увеличиваем количество детского товара в корзине на одну штуку
        cart_item.full_clean() #проверяем валидность данных в модели элемента корзины
        cart_item.save() #сохраняем изменения элемента корзины в базу данных
    except ValidationError:
        pass
    return redirect('cart_view') #перенаправляем пользователя на просмотр его корзины


def cart_update(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = CartItem.objects.get(id=item_id) #находим элемент корзины детских товаров по его id
        try:
            cart_item.quantity = quantity #обновляем поле количества детского товара в модели
            cart_item.full_clean() #запускаем встроенную валидацию полей модели
            cart_item.save() #сохраняем обновленный элемент детской корзины в базу данных
        except ValidationError:
            pass
    return redirect('cart_view') #перенаправляем обратно на страницу просмотра корзины


def cart_remove(request, item_id):
    cart_item = CartItem.objects.get(id=item_id) #находим нужный элемент детской корзины для его удаления
    cart_item.delete() #удаляем игрушку из корзины покупателя детского мира
    return redirect('cart_view') #перенаправляем обратно на страницу просмотра корзины


def about(request):
    return render(request, 'about.html') #открываем страницу информации об авторе детского мира


def info(request):
    return render(request, 'info.html') #открываем страницу информации о магазине детских товаров