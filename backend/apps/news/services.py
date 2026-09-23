from __future__ import annotations

from collections import Counter
from datetime import timedelta

from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.utils import timezone
from django.utils.text import slugify

from .models import Article, Author, Category, Tag
from .providers import get_providers
from .repositories import ArticleRepository, CATEGORY_ALIASES


DEMO_ARTICLES = [
    {
        "title": "Markets steady as central banks signal a slower path to rate cuts",
        "category": "Business",
        "summary": "Investors are recalibrating expectations after policymakers suggested inflation progress remains uneven across major economies.",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Markets", "Economy"],
    },
    {
        "title": "New battery factories reshape the race for affordable electric cars",
        "category": "Technology",
        "summary": "Automakers and suppliers are investing in regional battery capacity as demand shifts toward lower-cost electric vehicles.",
        "image_url": "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1600&q=85",
        "tags": ["EVs", "Manufacturing"],
    },
    {
        "title": "Art Basel brings fun back to the fair with the element of surprise",
        "category": "Art",
        "summary": "Collectors and curators say playful installations and unexpected collaborations are giving the fair a more open energy this season.",
        "image_url": "https://images.unsplash.com/photo-1545987796-200677ee1011?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Culture", "Art"],
    },
    {
        "title": "Climate researchers map new pressure points for coastal cities",
        "category": "Science",
        "summary": "Fresh modelling shows how infrastructure, housing and emergency services may need to adapt to compound flood risks.",
        "image_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Climate", "Cities"],
    },
    {
        "title": "Startups turn to practical AI tools after a year of experimentation",
        "category": "Startups",
        "summary": "Founders are focusing on workflow automation, support tooling and data cleanup as investors ask for clearer customer value.",
        "image_url": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1600&q=85",
        "tags": ["AI", "Startups"],
    },
    {
        "title": "Election officials expand verification systems ahead of busy voting year",
        "category": "Politics",
        "summary": "Local authorities are investing in staffing, cybersecurity and voter information systems to protect confidence in results.",
        "image_url": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Politics", "Elections"],
    },
    {
        "title": "A new generation of chefs is changing how restaurants source ingredients",
        "category": "Culture",
        "summary": "Independent kitchens are building closer relationships with regional producers while simplifying menus around seasonal supply.",
        "image_url": "https://images.unsplash.com/photo-1551218808-94e220e084d2?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Food", "Culture"],
    },
    {
        "title": "Airlines add routes as business travel returns in smaller bursts",
        "category": "Business",
        "summary": "Carriers are adjusting schedules around shorter trips, regional conferences and a more flexible corporate travel calendar.",
        "image_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Travel", "Business"],
    },
    {
        "title": "Scientists test low-cost sensors to improve air quality warnings",
        "category": "Science",
        "summary": "Pilot programs are combining community sensor networks with official monitoring to give residents faster local alerts.",
        "image_url": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Science", "Health"],
    },
    {
        "title": "Film festivals lean into smaller premieres and stronger local audiences",
        "category": "Culture",
        "summary": "Programmers are balancing global talent with regional storytelling as festivals compete for attention beyond red carpets.",
        "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Film", "Culture"],
    },
    {
        "title": "Cybersecurity teams prepare for faster attacks on cloud accounts",
        "category": "Technology",
        "summary": "Security leaders are prioritizing identity controls and monitoring as attackers automate credential theft and account takeover attempts.",
        "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Security", "Cloud"],
    },
    {
        "title": "Public transit agencies redesign stations for hotter summers",
        "category": "World",
        "summary": "Shade, ventilation and cooling materials are becoming central to station upgrades as cities adapt to more intense heat.",
        "image_url": "https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Cities", "Transport"],
    },
    {
        "title": "Women-led funds gain visibility as founders seek wider investor networks",
        "category": "Feminism",
        "summary": "A growing group of funds is backing overlooked founders while pushing the industry to measure access more transparently.",
        "image_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Funding", "Feminism"],
    },
    {
        "title": "Museums rethink membership programs for younger visitors",
        "category": "Art",
        "summary": "Institutions are adding flexible passes, evening events and digital benefits to build stronger relationships with new audiences.",
        "image_url": "https://images.unsplash.com/photo-1564399579883-451a5d44ec08?auto=format&fit=crop&w=1600&q=85",
        "tags": ["Museums", "Art"],
    },
]


class NewsIngestionService:
    def fetch_and_store(self) -> dict[str, int]:
        stats: dict[str, int] = {}
        for provider in get_providers():
            raw = provider.fetch_articles()
            stats[provider.__class__.__name__] = provider.save_articles(raw)
        return stats


class NewsQueryService:
    @staticmethod
    def normalize_category_aliases() -> None:
        for alias, target_name in CATEGORY_ALIASES.items():
            target_slug = slugify(target_name)
            alias_slug = slugify(alias)
            target = Category.objects.filter(slug=target_slug).first() or Category.objects.filter(name__iexact=target_name).first()

            duplicates = (
                Category.objects.filter(name__iexact=alias)
                | Category.objects.filter(slug=alias_slug)
            ).distinct()

            if target is None:
                target = duplicates.first()
                if target is None:
                    continue
                target.name = target_name
                target.slug = target_slug
                target.save(update_fields=["name", "slug"])

            if target.name != target_name or target.slug != target_slug:
                target.name = target_name
                target.slug = target_slug
                target.save(update_fields=["name", "slug"])

            for category in duplicates:
                if category.pk == target.pk:
                    continue
                Article.objects.filter(category=category).update(category=target)
                category.delete()

    @staticmethod
    def ensure_demo_content() -> int:
        NewsQueryService.normalize_category_aliases()

        if ArticleRepository.published().exists():
            return 0

        author = Author.objects.filter(slug="maria-nicholson").first()
        now = timezone.now()
        created = 0

        for index, item in enumerate(DEMO_ARTICLES):
            category, _ = Category.objects.get_or_create(
                name=item["category"],
                defaults={
                    "description": f"Latest {item['category']} news, reporting and analysis from FXLFM.",
                },
            )
            content = (
                f"{item['summary']}\n\n"
                "The story reflects the kind of clear, contextual reporting FXLFM publishes for readers who want the facts without unnecessary noise. "
                "Editors are watching how this development affects policy decisions, business planning and everyday life over the coming weeks.\n\n"
                "Further updates will focus on verified details, named sources and the practical consequences for communities, companies and institutions."
            )
            article, was_created = Article.objects.get_or_create(
                source_url=f"https://fxlfm.com/demo/{slugify(item['title'])}",
                defaults={
                    "title": item["title"],
                    "original_title": item["title"],
                    "original_content": content,
                    "rewritten_title": item["title"],
                    "rewritten_content": content,
                    "summary": item["summary"],
                    "seo_description": item["summary"][:320],
                    "source_name": "FXLFM Editorial",
                    "image_url": item["image_url"],
                    "category": category,
                    "author": author,
                    "status": Article.Status.PUBLISHED,
                    "published_at": now - timedelta(hours=index * 3),
                },
            )
            if was_created:
                created += 1

            for tag_name in item["tags"]:
                tag_slug = slugify(tag_name)[:100] or "tag"
                tag, _ = Tag.objects.get_or_create(
                    slug=tag_slug,
                    defaults={"name": tag_name},
                )
                article.tags.add(tag)

        return created

    @staticmethod
    def trending(limit: int = 8):
        NewsQueryService.ensure_demo_content()
        return ArticleRepository.published().annotate(tag_count=Count("tags")).order_by("-tag_count", "-published_at")[:limit]

    @staticmethod
    def popular_categories(limit: int = 6) -> list[dict[str, int | str]]:
        data = (
            ArticleRepository.published()
            .values("category__name")
            .annotate(total=Count("id"))
            .order_by("-total")[:limit]
        )
        return [{"name": item["category__name"] or "General", "total": item["total"]} for item in data]

    @staticmethod
    def related(article: Article, limit: int = 4):
        tag_ids = [tag.id for tag in article.tags.all()]
        queryset = ArticleRepository.published().exclude(pk=article.pk)

        if tag_ids:
            queryset = queryset.annotate(
                matching_tags=Count(
                    "tags",
                    filter=Q(tags__id__in=tag_ids),
                    distinct=True,
                )
            )
        else:
            queryset = queryset.annotate(matching_tags=Value(0, output_field=IntegerField()))

        queryset = queryset.annotate(
            category_match=Case(
                When(category_id=article.category_id, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        return (
            queryset.select_related("category")
            .order_by("-matching_tags", "-category_match", "-published_at", "-created_at")[:limit]
        )


class NewsCleanupService:
    @staticmethod
    def cleanup_duplicates() -> int:
        seen = Counter()
        deleted = 0
        for article in Article.objects.order_by("source_url", "id"):
            seen[article.source_url] += 1
            if seen[article.source_url] > 1:
                article.delete()
                deleted += 1
        return deleted
