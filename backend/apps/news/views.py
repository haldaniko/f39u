from __future__ import annotations

from django.db.models import Q
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Article, Author, Category, Tag
from .serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    AdminArticleSerializer,
    AuthorDetailSerializer,
    CategorySerializer,
    TagSerializer,
)
from .services import NewsQueryService


def health_view(request):
    return JsonResponse({"status": "ok"})


class ArticleViewSet(ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    search_fields = ["title", "summary", "rewritten_content"]

    def get_queryset(self):
        return (
            Article.objects.filter(status=Article.Status.PUBLISHED)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return ArticleListSerializer

    @action(detail=True, methods=["get"])
    def related(self, request, slug=None):
        article = self.get_object()
        queryset = NewsQueryService.related(article, limit=4)
        return Response(ArticleListSerializer(queryset, many=True).data)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class AuthorViewSet(ReadOnlyModelViewSet):
    queryset = Author.objects.all().order_by("name")
    serializer_class = AuthorDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def search_view(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response([])
    queryset = Article.objects.filter(
        status=Article.Status.PUBLISHED
    ).filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(rewritten_content__icontains=query))
    return Response(ArticleListSerializer(queryset[:20], many=True).data)


class TrendingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        queryset = NewsQueryService.trending(limit=10)
        return Response(ArticleListSerializer(queryset, many=True).data)


class AdminArticleViewSet(ModelViewSet):
    serializer_class = AdminArticleSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["title", "summary", "source_name", "slug"]
    ordering_fields = ["created_at", "updated_at", "published_at", "title"]
    ordering = ["-updated_at"]
    filterset_fields = ["status", "category", "author"]

    def get_queryset(self):
        return (
            Article.objects.all()
            .select_related("category", "author")
            .prefetch_related("tags")
        )


class AdminArticleOptionsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response(
            {
                "statuses": [
                    {"value": value, "label": label}
                    for value, label in Article.Status.choices
                ],
                "categories": list(Category.objects.order_by("name").values("id", "name", "slug")),
                "authors": list(Author.objects.order_by("name").values("id", "name", "slug")),
                "tags": list(Tag.objects.order_by("name").values("id", "name", "slug")),
            }
        )
