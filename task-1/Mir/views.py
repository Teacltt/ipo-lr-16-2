from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Category, Manufacturer, Product

def detmir(request):
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    products = Product.objects.all()
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products
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
                error_message = e.message_dict['price'][0]
            elif 'stock' in e.message_dict:
                error_message = e.message_dict['stock'][0]
            else:
                error_message = "Ошибка валидации данных!"
        except ValueError:
            error_message = "Введите корректные числовые значения!"

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    return render(request, 'admin_panel.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'error_message': error_message,
        'success_message': success_message
    })

def author(request):
    return render(request, 'author.html')

def shop(request):
    return render(request, 'shop.html')