from django.db import models
class Author(models.Model):
    name =  models.CharField(max_length=50,verbose_name='Author Name')
    bio = models.CharField(max_length=200,verbose_name="Author's Bio")
    dob = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ({self.dob})"
    