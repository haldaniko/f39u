from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, CategoryViewSet, TagViewSet, TrendingView, search_view

router = DefaultRouter()
router.register(r"", ArticleViewSet, basename="article")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("search/", search_view, name="search"),
    path("trending/", TrendingView.as_view(), name="trending"),
    path("", include(router.urls)),
]
