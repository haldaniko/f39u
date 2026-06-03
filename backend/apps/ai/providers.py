from __future__ import annotations

import os
from abc import ABC, abstractmethod


class AIRewriter(ABC):
    @abstractmethod
    def rewrite(self, article: dict[str, str]) -> dict[str, str | list[str]]:
        raise NotImplementedError


class FallbackRewriter(AIRewriter):
    def rewrite(self, article: dict[str, str]) -> dict[str, str | list[str]]:
        title = article.get("title", "Untitled")
        content = article.get("content", "")
        summary = content[:220].strip() if content else "No summary available"
        rewritten_body = f"{content}\n\nThis story was editorially rewritten for clarity and structure."
        return {
            "title": f"AI Brief: {title}",
            "summary": summary,
            "body": rewritten_body,
            "seo_description": summary[:160],
            "tags": ["ai-rewrite", "news"],
        }


class OpenAIRewriter(FallbackRewriter):
    pass


class AnthropicRewriter(FallbackRewriter):
    pass


class GeminiRewriter(FallbackRewriter):
    pass


class OpenRouterRewriter(FallbackRewriter):
    pass


def get_ai_rewriter() -> AIRewriter:
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    mapping = {
        "openai": OpenAIRewriter,
        "anthropic": AnthropicRewriter,
        "gemini": GeminiRewriter,
        "openrouter": OpenRouterRewriter,
    }
    return mapping.get(provider, FallbackRewriter)()
