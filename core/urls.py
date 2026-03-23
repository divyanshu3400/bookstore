from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import BookAPIView,AuthorAPIView,CategoryAPIView

router = DefaultRouter()

router.register(r"categories",CategoryAPIView, basename="category")
router.register(r"authors",AuthorAPIView, basename="author")
router.register(r"books",BookAPIView, basename="book")
urlpatterns = [
    path('', include(router.urls)),
]