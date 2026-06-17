from rest_framework import serializers
from .models import Category, Manufacturer, Product, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category #указываем базовую модель категорий для преобразования данных
        fields = '__all__' #подключаем автоматическую сериализацию всех доступных полей модели


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer #указываем базовую модель производителей для преобразования данных
        fields = '__all__' #подключаем автоматическую сериализацию всех доступных полей модели


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product #указываем базовую модель товаров для преобразования данных
        fields = '__all__' #подключаем автоматическую сериализацию всех доступных полей модели


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem #указываем базовую модель элементов корзины для преобразования данных
        fields = '__all__' #подключаем автоматическую сериализацию всех доступных полей модели


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True) #подключаем список вложенных элементов корзины через сериализатор

    class Meta:
        model = Cart #указываем базовую модель корзин для преобразования данных
        fields = '__all__' #подключаем автоматическую сериализацию всех доступных полей модели