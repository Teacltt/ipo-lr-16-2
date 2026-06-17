from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem #импортируем все модели детского мира по заданию пятого пункта

admin.site.register(Category) #регистрируем категории детских товаров в админ-панели Django по заданию
admin.site.register(Manufacturer) #регистрируем производителей игрушек в админ-панели Django по заданию
admin.site.register(Product) #регистрируем детские товары в админ-панели Django по заданию
admin.site.register(Cart) #регистрируем корзины покупателей в админ-панели Django по заданию
admin.site.register(CartItem) #регистрируем элементы детских корзин в админ-панели Django по заданию