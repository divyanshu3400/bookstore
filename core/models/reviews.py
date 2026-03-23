from django.db import models
from django.contrib.auth import get_user_model
from .books import Book
User  = get_user_model()

class Reviews(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="reviews")
    name = models.CharField(max_length=100)
    book = models.ForeignKey(Book,on_delete=models.CASCADE,related_name="books_reviews")
    comment = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.name} ({self.rating})"
    
    def save(self):
        if self.user:
            self.name = self.user.get_full_name()
        return super().save()
