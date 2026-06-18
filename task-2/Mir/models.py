from django.db import models
from django.contrib.auth.models import User #импортируем пользователя
from django.core.exceptions import ValidationError #импортируем валидацию


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание категории")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название производителя")
    country = models.CharField(max_length=100, verbose_name="Страна")
    description = models.TextField(blank=True, null=True, verbose_name="Описание производителя")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Подробное описание товара")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.IntegerField(verbose_name="Количество на складе")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")

    def __str__(self):
        return self.name

    def clean(self):
        if self.price is not None and self.price < 0:
            raise ValidationError({'price': 'Цена не может быть отрицательной!'})
        if self.stock is not None and self.stock < 0:
            raise ValidationError({'stock': 'Количество на складе не может быть отрицательным!'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь") #каскадное удаление по тз
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания") #автоматическая дата по тз

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def total_cost(self):
        return sum(item.element_cost() for item in self.items.all()) #общая стоимость по тз

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина") #связь с корзиной по тз
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар") #связь с товаром по тз
    quantity = models.PositiveIntegerField(verbose_name="Количество") #количество по тз

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"

    def element_cost(self):
        return self.product.price * self.quantity #стоимость элемента по тз

    def clean(self):
        if self.product and self.quantity > self.product.stock:
            raise ValidationError({'quantity': f'Количество не должно превышать остаток на складе ({self.product.stock} шт.)!'}) #валидация остатков по тз

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"