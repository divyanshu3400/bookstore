from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import BookAPIView,AuthorAPIView,CategoryAPIView,BookDetailAPIView,OrdersViewSet

router = DefaultRouter()

router.register(r"categories",CategoryAPIView, basename="category")
router.register(r"authors",AuthorAPIView, basename="author")
router.register(r"orders",OrdersViewSet, basename="order")
urlpatterns = [
    path('', include(router.urls)),
    path('books/',BookAPIView.as_view(),name="book"),
    path('books/<int:pk>',BookDetailAPIView.as_view(),name="book")
]