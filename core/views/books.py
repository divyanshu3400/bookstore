from ..models import Book,Category,Author
from rest_framework.permissions import AllowAny
from ..serializers import BookSerializer,BookListSerializer,AuthSerializer,CategorySerializer
from .base import BaseModelViewSet

from rest_framework.generics import ListAPIView,RetrieveAPIView

class AuthorAPIView(BaseModelViewSet):
    permission_classes = [AllowAny]
    queryset = Author.objects.all()
    serializer_class = AuthSerializer 
    


class CategoryAPIView(BaseModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 
    


class BookAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookListSerializer
    
    def get_queryset(self):
        qs = Book.objects.select_related("author").prefetch_related("category")
        return  qs
    
        
class BookDetailAPIView(RetrieveAPIView):
    serializer_class = BookSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        qs = Book.objects.select_related("author").prefetch_related("category")
        return  qs
    
        