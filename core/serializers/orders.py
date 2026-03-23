from ..models import Orders,OrderItem
from rest_framework import serializers

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            
        )

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source = "order_items",many=True)
    
    class Meta:
        model = Orders
        fields = (
            "order_no",
            "customer",
            "customer_name",
            "customer_email",
            "items",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("order_no","created_at","updated_at")
        
