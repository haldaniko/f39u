from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.analytics.views import AdminStatisticsView
from apps.news.views import CategoryViewSet, TagViewSet, TrendingView, search_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/news/", include("apps.news.urls")),
    path("api/categories/", CategoryViewSet.as_view({"get": "list"}), name="categories-list"),
    path("api/tags/", TagViewSet.as_view({"get": "list"}), name="tags-list"),
    path("api/search/", search_view, name="search"),
    path("api/trending/", TrendingView.as_view(), name="trending"),
    path("api/admin/statistics/", AdminStatisticsView.as_view(), name="admin-statistics"),
    path("api/ai/", include("apps.ai.urls")),
    path("api/auth/", include("apps.users.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
]
