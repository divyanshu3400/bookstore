from ..models import Orders
from rest_framework.permissions import AllowAny
from .base import BaseModelViewSet
from ..serializers import OrderSerializer


        
class OrdersViewSet(BaseModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Orders.objects.select_related("customer").prefetch_related("order_items")
    
