from __future__ import annotations

import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any

import requests


logger = logging.getLogger(__name__)


class AIRewriter(ABC):
    @abstractmethod
    def rewrite(self, article: dict[str, str]) -> dict[str, str | list[str]]:
        raise NotImplementedError


class FallbackRewriter(AIRewriter):
    def rewrite(self, article: dict[str, str]) -> dict[str, str | list[str]]:
        title = article.get("title", "Untitled")
        content = article.get("content", "")
        summary = content[:220].strip() if content else "No summary available"
        rewritten_body = content
        return {
            "title": title,
            "summary": summary,
            "body": rewritten_body,
            "seo_description": summary[:160],
            "tags": ["news", "analysis"],
            "_fallback": "true",
        }


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid integer for %s=%s. Falling back to %s", name, raw, default)
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning("Invalid float for %s=%s. Falling back to %s", name, raw, default)
        return default


def _extract_json_from_text(text: str) -> dict[str, Any]:
    normalized = text.strip()
    if normalized.startswith("```"):
        lines = normalized.splitlines()
        if len(lines) >= 3:
            normalized = "\n".join(lines[1:-1]).strip()

    first = normalized.find("{")
    last = normalized.rfind("}")
    if first == -1 or last == -1 or first >= last:
        raise ValueError("Model response does not contain a JSON object")

    candidate = normalized[first : last + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        sanitized = _escape_control_chars_in_json_strings(candidate)
        return json.loads(sanitized)


def _escape_control_chars_in_json_strings(raw: str) -> str:
    escaped: list[str] = []
    in_string = False
    is_escaped = False

    for ch in raw:
        if in_string:
            if is_escaped:
                escaped.append(ch)
                is_escaped = False
                continue

            if ch == "\\":
                escaped.append(ch)
                is_escaped = True
                continue

            if ch == '"':
                escaped.append(ch)
                in_string = False
                continue

            if ch == "\n":
                escaped.append("\\n")
                continue
            if ch == "\r":
                escaped.append("\\r")
                continue
            if ch == "\t":
                escaped.append("\\t")
                continue

            if ord(ch) < 0x20:
                escaped.append(f"\\u{ord(ch):04x}")
                continue

            escaped.append(ch)
            continue

        escaped.append(ch)
        if ch == '"':
            in_string = True

    return "".join(escaped)


def _normalize_openrouter_result(payload: dict[str, Any], title: str, content: str) -> dict[str, str | list[str]]:
    summary_fallback = content[:220].strip() if content else "No summary available"

    rewritten_title = str(payload.get("title") or title)[:300]
    rewritten_body = _format_article_body(str(payload.get("body") or content))
    rewritten_summary = _strip_teaser_phrases(str(payload.get("summary") or summary_fallback))
    seo_description = str(payload.get("seo_description") or rewritten_summary[:160])[:320]

    raw_tags = payload.get("tags", [])
    if isinstance(raw_tags, list):
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()][:8]
    else:
        tags = ["news", "analysis"]

    if not tags:
        tags = ["news", "analysis"]

    return {
        "title": rewritten_title,
        "summary": rewritten_summary,
        "body": rewritten_body,
        "seo_description": seo_description,
        "tags": tags,
        "_fallback": "false",
    }


def _extract_message_text(message_content: Any) -> str:
    if isinstance(message_content, str):
        return message_content
    if isinstance(message_content, list):
        parts: list[str] = []
        for item in message_content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()
    return str(message_content)


def _strip_teaser_phrases(text: str) -> str:
    value = (text or "").strip()
    if not value:
        return ""

    patterns = [
        r"\bread the full story\b.*$",
        r"\bread more\b.*$",
        r"\bcontinue reading\b.*$",
        r"\bfull article\b.*$",
        r"\bclick here\b.*$",
        r"\bvisit (the )?original\b.*$",
        r"\boriginally published at\b.*$",
    ]

    lines = [line.strip() for line in value.splitlines() if line.strip()]
    cleaned_lines: list[str] = []
    for line in lines:
        normalized = line
        for pattern in patterns:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE).strip(" -:")
        if normalized:
            cleaned_lines.append(normalized)
    return "\n\n".join(cleaned_lines).strip()


def _format_article_body(text: str) -> str:
    value = _strip_teaser_phrases(text)
    if not value:
        return ""

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n+", value) if paragraph.strip()]
    if len(paragraphs) >= 2:
        return "\n\n".join(paragraphs)

    sentences = re.split(r"(?<=[.!?])\s+", paragraphs[0] if paragraphs else value)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    if len(sentences) < 6:
        return value

    grouped = [
        " ".join(sentences[index : index + 3]).strip()
        for index in range(0, len(sentences), 3)
    ]
    return "\n\n".join(paragraph for paragraph in grouped if paragraph)


class OpenAIRewriter(FallbackRewriter):
    pass


class AnthropicRewriter(FallbackRewriter):
    pass


class GeminiRewriter(FallbackRewriter):
    pass


class OpenRouterRewriter(FallbackRewriter):
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.endpoint = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.timeout = _env_int("OPENROUTER_TIMEOUT", 45)
        self.max_input_chars = _env_int("OPENROUTER_MAX_INPUT_CHARS", 12000)
        self.max_output_tokens = _env_int("OPENROUTER_MAX_OUTPUT_TOKENS", 2200)
        self.temperature = _env_float("OPENROUTER_TEMPERATURE", 0.3)
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "").strip()
        self.app_name = os.getenv("OPENROUTER_APP_NAME", "Future Xclusive Local and Foreign Media")

    def rewrite(self, article: dict[str, str]) -> dict[str, str | list[str]]:
        title = article.get("title", "Untitled")
        content = article.get("content", "")

        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY is empty. Falling back to local rewriter.")
            return super().rewrite(article)

        user_prompt = (
            "Rewrite this article as a complete publication-ready story and return only JSON with fields "
            "title, summary, body, seo_description, tags. "
            "Rules: title <= 300 chars, seo_description <= 320 chars, tags must be an array of short strings. "
            "Detect the source language; if it is not English, translate the final title, summary, body, and seo_description into English. "
            "Write a fuller article with 5 to 7 concise paragraphs when the provided facts support it. "
            "Separate each paragraph with a blank line. Do not use markdown headings, bullets, or numbered lists. "
            "Remove teaser phrases like 'Read the full story', 'Read more', 'Continue reading'. "
            "If the source text is partial, expand it into a coherent full article using only the provided facts. "
            "You may add neutral context, transitions, and conclusions, but do not invent events, names, dates, "
            "quotes, numbers, or unverifiable claims. Do not mention AI or rewriting process in the output.\n\n"
            f"ORIGINAL_TITLE:\n{title}\n\n"
            f"ORIGINAL_CONTENT:\n{content[: self.max_input_chars]}"
        )

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_output_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional newsroom writer. "
                        "Always answer with valid JSON only, with keys: "
                        "title, summary, body, seo_description, tags. "
                        "Never include labels such as AI-written, AI-driven, rewritten by AI, or similar notes."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            response_data = response.json()
            message_content = response_data["choices"][0]["message"]["content"]
            parsed = _extract_json_from_text(_extract_message_text(message_content))
            return _normalize_openrouter_result(parsed, title=title, content=content)
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenRouter rewrite failed: %s. Falling back to local rewriter.", exc)
            return super().rewrite(article)


def get_ai_rewriter() -> AIRewriter:
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    mapping = {
        "openai": OpenAIRewriter,
        "anthropic": AnthropicRewriter,
        "gemini": GeminiRewriter,
        "openrouter": OpenRouterRewriter,
    }
    return mapping.get(provider, FallbackRewriter)()
