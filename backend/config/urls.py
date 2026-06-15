from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.analytics.views import AdminStatisticsView
from apps.news.sitemap_views import robots_txt
from apps.news.sitemaps import sitemaps
from apps.news.seo_views import about_page, article_page, category_page, contact_page, search_page
from apps.news.views import CategoryViewSet, TagViewSet, TrendingView, search_view

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots-txt"),
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
    path("article/<slug:slug>", article_page, name="article-page"),
    path("article/<slug:slug>/", article_page),
    path("category/<slug:slug>", category_page, name="category-page"),
    path("category/<slug:slug>/", category_page),
    path("about", about_page, name="about-page"),
    path("about/", about_page),
    path("contact", contact_page, name="contact-page"),
    path("contact/", contact_page),
    path("search", search_page, name="search-page"),
    path("search/", search_page),
]
