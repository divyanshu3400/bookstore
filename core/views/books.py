from ..models import Book,Category,Author
from rest_framework.permissions import AllowAny
from ..serializers import BookSerializer,BookListSerializer,AuthSerializer,CategorySerializer
from .base import BaseModelViewSet

class AuthorAPIView(BaseModelViewSet):
    permission_classes = [AllowAny]
    queryset = Author.objects.all()
    serializer_class = AuthSerializer 
    


class CategoryAPIView(BaseModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 
    


class BookAPIView(BaseModelViewSet):
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        qs = Book.objects.select_related("author").prefetch_related("category")
        return  qs
    
    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            return BookListSerializer
        else:
            return BookSerializer
        
    
