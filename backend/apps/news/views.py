from __future__ import annotations

from django.http import JsonResponse
from django.db.models import Case, Count, IntegerField, Q, Value, When

from .categories import CANONICAL_CATEGORY_SLUGS
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Article, Author, Category, NewsletterSubscriber, Tag
from .serializers import (
    AdminAuthorSerializer,
    AdminNewsletterSubscriberSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    AdminArticleSerializer,
    AuthorDetailSerializer,
    CategorySerializer,
    NewsletterSubscribeSerializer,
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
        NewsQueryService.ensure_demo_content()
        queryset = (
            Article.objects.filter(status=Article.Status.PUBLISHED)
            .select_related("category", "author")
            .prefetch_related("categories", "tags")
        )
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(Q(category__slug=category) | Q(categories__slug=category)).distinct()
        return queryset

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
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self):
        NewsQueryService.ensure_demo_content()
        NewsQueryService.normalize_category_aliases()
        order = Case(
            *[
                When(slug=slug, then=Value(index))
                for index, slug in enumerate(CANONICAL_CATEGORY_SLUGS)
            ],
            default=Value(len(CANONICAL_CATEGORY_SLUGS)),
            output_field=IntegerField(),
        )
        return (
            Category.objects.filter(slug__in=CANONICAL_CATEGORY_SLUGS)
            .annotate(total=Count("categorized_articles", filter=Q(categorized_articles__status=Article.Status.PUBLISHED), distinct=True))
            .order_by(order)
        )


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        NewsQueryService.ensure_demo_content()
        return Tag.objects.all().order_by("name")


class AuthorViewSet(ReadOnlyModelViewSet):
    serializer_class = AuthorDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        NewsQueryService.ensure_demo_content()
        return Author.objects.all().order_by("name")


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def search_view(request):
    NewsQueryService.ensure_demo_content()
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response([])
    queryset = Article.objects.filter(
        status=Article.Status.PUBLISHED,
        title__icontains=query,
    )
    return Response(ArticleListSerializer(queryset[:20], many=True).data)


class TrendingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        queryset = NewsQueryService.trending(limit=10)
        return Response(ArticleListSerializer(queryset, many=True).data)


class NewsletterSubscribeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = NewsletterSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        source = serializer.validated_data["source"]
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={"source": source},
        )

        if not created:
            changed_fields = []
            if subscriber.email != email:
                subscriber.email = email
                changed_fields.append("email")
            if subscriber.source != source:
                subscriber.source = source
                changed_fields.append("source")
            if not subscriber.is_active:
                subscriber.is_active = True
                changed_fields.append("is_active")
            if changed_fields:
                changed_fields.append("updated_at")
                subscriber.save(update_fields=changed_fields)

        return Response(
            {"message": "You are subscribed to the FXLFM newsletter."},
            status=201 if created else 200,
        )


class AdminArticleViewSet(ModelViewSet):
    serializer_class = AdminArticleSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["title", "summary", "source_name", "slug"]
    ordering_fields = ["created_at", "updated_at", "published_at", "title"]
    ordering = ["-updated_at"]
    filterset_fields = ["status", "author"]

    def get_queryset(self):
        queryset = (
            Article.objects.all()
            .select_related("category", "author")
            .prefetch_related("categories", "tags")
        )
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(Q(category_id=category_id) | Q(categories__id=category_id)).distinct()
        return queryset


class AdminAuthorViewSet(ModelViewSet):
    serializer_class = AdminAuthorSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    search_fields = ["name", "job_title", "bio", "location"]
    ordering_fields = ["name", "joined_at"]
    ordering = ["name"]
    queryset = Author.objects.all()


class AdminNewsletterSubscriberViewSet(ModelViewSet):
    serializer_class = AdminNewsletterSubscriberSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["email"]
    ordering_fields = ["email", "subscribed_at", "updated_at"]
    ordering = ["-subscribed_at"]
    filterset_fields = ["source", "is_active"]
    http_method_names = ["get", "patch", "delete", "head", "options"]
    queryset = NewsletterSubscriber.objects.all()


class AdminArticleOptionsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        NewsQueryService.normalize_category_aliases()
        category_order = Case(
            *[
                When(slug=slug, then=Value(index))
                for index, slug in enumerate(CANONICAL_CATEGORY_SLUGS)
            ],
            default=Value(len(CANONICAL_CATEGORY_SLUGS)),
            output_field=IntegerField(),
        )
        return Response(
            {
                "statuses": [
                    {"value": value, "label": label}
                    for value, label in Article.Status.choices
                ],
                "categories": list(Category.objects.filter(slug__in=CANONICAL_CATEGORY_SLUGS).order_by(category_order).values("id", "name", "slug")),
                "authors": list(Author.objects.order_by("name").values("id", "name", "slug")),
            }
        )
