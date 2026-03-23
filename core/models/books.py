from django.db import models
from .author import Author

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    
    
    
class Book(models.Model):
    author = models.ForeignKey(Author,on_delete=models.SET_NULL,null=True,related_name='books')
    category = models.ManyToManyField(Category)
    title =  models.CharField(max_length=100, verbose_name="Book Title")
    ISBN = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(default=0.0, verbose_name="Book's Price",decimal_places=2,max_digits=5)
    pub_date = models.DateField()
    is_active = models.BooleanField(default=False)
    stock_qty = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}-({self.price})"
    