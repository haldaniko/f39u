from __future__ import annotations

import os

from django.http import HttpResponse


SITE_URL = os.getenv("SITE_URL", "https://fxlfm.com").rstrip("/")


def robots_txt(request) -> HttpResponse:
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /django-admin/",
            "Disallow: /api/",
            f"Sitemap: {SITE_URL}/sitemap.xml",
            "",
        ]
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
