from ..models import Book,Author,Category
from rest_framework import serializers

class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id","name")

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]

class BookListSerializer(serializers.ModelSerializer):
    author = AuthSerializer(many=True)
    category = CategorySerializer(many=True)
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "ISBN",
            "price",
            "author",
            "category",
            ]

class BookSerializer(serializers.ModelSerializer):
    # author = AuthSerializer(many=True)
    # category = CategorySerializer(many=True)
    class Meta:
        model = Book
        fields = ("id")