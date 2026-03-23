from django.db import models
from django.contrib.auth import get_user_model
from .books import Book
User  = get_user_model()

# pending → confirmed → shipped → delivered. Orders can also be cancelled. 
class OrderStatus(models.TextChoices):
    PENDING = 'pending',"Pending"
    CONFIRMED = 'confirmed', "Confirmed"
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered',"Delivered"
    

class Orders(models.Model):
    order_no = models.UUIDField(primary_key=True)
    customer = models.ForeignKey(User,on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=500)
    customer_email = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} {self.order_no}"
    
    def save(self):
        if self.customer:
            self.customer_name = self.customer.get_full_name()
            self.customer_email = self.customer.emai
        return super().save()
    
class OrderItem(models.Model):
    order = models.ForeignKey(Orders,on_delete=models.CASCADE, related_name="order_items")
    book = models.ForeignKey(Book,on_delete=models.CASCADE, related_name="ordered_books")
    purchased_qty= models.IntegerField(default=0)
    price = models.DecimalField(default=0.0,decimal_places=2,max_digits=5)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_id} - {self.book.title} - ${self.price}"   
    
    def save(self):
        if self.book:
            self.price= self.book.price
        return super().save()