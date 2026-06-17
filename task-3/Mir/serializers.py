from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile

class ProfileSerializer(serializers.ModelSerializer):
    # Сериализатор профиля покупателя «Детского мира» (Задание 3, пункты 1 и 2)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'role', 'full_name', 'phone', 'address']
        read_only_fields = ['id', 'role'] # Защита роли от несанкционированного изменения клиентом

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
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