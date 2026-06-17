from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100) #название категории детских товаров в базе данных
    description = models.TextField(blank=True, null=True) #подробное описание категории детских товаров

    def __str__(self):
        return self.name #отображение названия категории детских товаров в панели администратора


class Manufacturer(models.Model):
    name = models.CharField(max_length=100) #название завода или бренда детских товаров в базе данных
    country = models.CharField(max_length=100) #страна производства детских товаров и игрушек
    description = models.TextField(blank=True, null=True) #подробное описание завода или бренда детских товаров

    def __str__(self):
        return self.name #отображение названия бренда детских товаров в панели администратора


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products') #связь товара с категорией детских товаров
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='products') #связь товара с брендом детских товаров
    name = models.CharField(max_length=200) #полное название детского товара или игрушки в базе данных
    description = models.TextField() #подробное описание характеристик детского товара
    price = models.DecimalField(max_length=10, max_digits=10, decimal_places=2) #точная стоимость детского товара в валюте BYN
    stock = models.PositiveIntegerField() #доступное количество детского товара на складе магазина

    def __str__(self):
        return self.name #отображение названия детского товара в панели администратора


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart') #связь личной корзины с конкретным пользователем
    created_at = models.DateTimeField(auto_now_add=True) #дата и точное время создания корзины в базе данных

    @property
    def total_cost(self):
        return sum(item.element_cost for item in self.items.all()) #вычисление полной стоимости всех детских товаров в корзине пользователя


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items') #привязка элемента к конкретной корзине пользователя
    product = models.ForeignKey(Product, on_delete=models.CASCADE) #привязка элемента к конкретному детскому товару из базы
    quantity = models.PositiveIntegerField(default=1) #поле количества товара в корзине с начальным значением один

    def clean(self):
        if self.quantity > self.product.stock: #проверяем превышает ли количество остаток товара на складе магазина
            raise ValidationError({'quantity': f"Количество не должно превышать остаток на складе ({self.product.stock} шт.)!"}) #выбрасываем ошибку валидации

    def save(self, *args, **kwargs):
        self.full_clean() #принудительно запускаем валидацию метода clean перед сохранением в базу данных
        super().save(*args, **kwargs) #вызываем стандартное сохранение объекта модели в базу данных

    @property
    def element_cost(self):
        return self.product.price * self.quantity #вычисляем общую стоимость этой позиции товара в корзине детского мира


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders') #привязка заказа к конкретному авторизованному пользователю
    created_at = models.DateTimeField(auto_now_add=True) #дата и точное время автоматического создания заказа в базе данных
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) #итоговая сумма к оплате по чеку заказа

    def __str__(self):
        return f"Заказ №{self.id} пользователя {self.user.username}" #отображение информации о заказе в панели администратора Django


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items') #привязка элемента к конкретному номеру заказа пользователя
    product = models.ForeignKey(Product, on_delete=models.CASCADE) #привязка элемента к конкретному купленному детскому товару
    price = models.DecimalField(max_digits=10, decimal_places=2) #фиксация точной цены товара на момент оформления заказа
    quantity = models.PositiveIntegerField(default=1) #количество выкупленного детского товара в текущем заказе пользователя

    @property
    def element_cost(self):
        return self.price * self.quantity #вычисление итоговой стоимости этой позиции товара внутри оформленного заказа
