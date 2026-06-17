from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    # Поле открыто для записи для смены Email по заданию (Пункт 3)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = Profile
        # Добавляем новые специфичные поля в список вывода API (Пункт 1)
        fields = ['id', 'username', 'email', 'role', 'full_name', 'phone', 'address', 'child_age', 'bonus_card']
        read_only_fields = ['id', 'role']

    def update(self, instance, validated_data):
        # Переопределение для сохранения Email во встроенную модель User
        user_data = validated_data.pop('user', {})
        new_email = user_data.get('email')
        
        if new_email is not None:
            user = instance.user
            user.email = new_email
            user.save()
            
        return super().update(instance, validated_data)

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
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_cost', 'created_at', 'items']