from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile

class ProfileSerializer(serializers.ModelSerializer):
    # Сериализатор расширенного профиля пользователя (Задание 3, пункты 1 и 2)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'role', 'full_name', 'phone', 'address']
        read_only_fields = ['id', 'role'] # Защита роли от несанкционированного изменения клиентом

class CategorySerializer(serializers.ModelSerializer):
    # Преобразователь категорий детских товаров в формат JSON
    class Meta:
        model = Category
        fields = '__all__'

class ManufacturerSerializer(serializers.ModelSerializer):
    # Преобразователь брендов детской продукции в формат JSON
    class Meta:
        model = Manufacturer
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    # Преобразователь ассортимента игрушек на складе в формат JSON
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_cost']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    # Вложенный сериализатор для вывода состава детских чеков
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_cost', 'created_at', 'items']