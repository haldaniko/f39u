import { useEffect } from "react";

const SITE_NAME = "FXLFM";
const DEFAULT_SITE_URL = "https://fxlfm.com";
const SITE_URL = (import.meta.env.VITE_SITE_URL || DEFAULT_SITE_URL).replace(/\/$/, "");

function cleanText(value) {
  return String(value || "")
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function truncate(value, maxLength) {
  const text = cleanText(value);

  if (text.length <= maxLength) {
    return text;
  }

  const shortened = text.slice(0, maxLength - 3);
  const lastSpace = shortened.lastIndexOf(" ");
  return `${shortened.slice(0, lastSpace > maxLength * 0.7 ? lastSpace : undefined).trim()}...`;
}

function truncateTitle(value) {
  const title = cleanText(value);
  const brandSuffix = ` | ${SITE_NAME}`;

  if (!title.endsWith(brandSuffix)) {
    return truncate(title, 70);
  }

  const unbrandedTitle = title.slice(0, -brandSuffix.length);
  return `${truncate(unbrandedTitle, 70 - brandSuffix.length)}${brandSuffix}`;
}

export function absoluteUrl(value) {
  if (!value) {
    return "";
  }

  try {
    return new URL(value, SITE_URL).toString();
  } catch {
    return "";
  }
}

function setMeta(selector, attributes) {
  let element = document.head.querySelector(selector);

  if (!element) {
    element = document.createElement("meta");
    document.head.appendChild(element);
  }

  Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value));
}

function setCanonical(href) {
  let element = document.head.querySelector('link[rel="canonical"]');

  if (!element) {
    element = document.createElement("link");
    element.setAttribute("rel", "canonical");
    document.head.appendChild(element);
  }

  element.setAttribute("href", href);
}

function removeMeta(selector) {
  document.head.querySelector(selector)?.remove();
}

function setStructuredData(structuredData) {
  const selector = 'script[data-seo-structured-data="true"]';
  let element = document.head.querySelector(selector);

  if (!structuredData) {
    element?.remove();
    return;
  }

  if (!element) {
    element = document.createElement("script");
    element.type = "application/ld+json";
    element.dataset.seoStructuredData = "true";
    document.head.appendChild(element);
  }

  element.textContent = JSON.stringify(structuredData);
}

export default function Seo({
  title,
  description,
  path = "/",
  image,
  type = "website",
  publishedAt,
  structuredData,
  noindex = false,
}) {
  useEffect(() => {
    const pageTitle = truncateTitle(title);
    const pageDescription = truncate(
      description || "Read the latest global news, reporting and analysis from FXLFM.",
      160
    );
    const canonicalUrl = absoluteUrl(path);
    const imageUrl = absoluteUrl(image);

    document.title = pageTitle;
    setMeta('meta[name="description"]', { name: "description", content: pageDescription });
    setMeta('meta[name="robots"]', {
      name: "robots",
      content: noindex ? "noindex, follow" : "index, follow, max-image-preview:large",
    });
    setMeta('meta[property="og:site_name"]', { property: "og:site_name", content: SITE_NAME });
    setMeta('meta[property="og:type"]', { property: "og:type", content: type });
    setMeta('meta[property="og:title"]', { property: "og:title", content: pageTitle });
    setMeta('meta[property="og:description"]', { property: "og:description", content: pageDescription });
    setMeta('meta[property="og:url"]', { property: "og:url", content: canonicalUrl });
    setMeta('meta[name="twitter:card"]', {
      name: "twitter:card",
      content: imageUrl ? "summary_large_image" : "summary",
    });
    setMeta('meta[name="twitter:title"]', { name: "twitter:title", content: pageTitle });
    setMeta('meta[name="twitter:description"]', { name: "twitter:description", content: pageDescription });
    setCanonical(canonicalUrl);

    if (imageUrl) {
      setMeta('meta[property="og:image"]', { property: "og:image", content: imageUrl });
      setMeta('meta[name="twitter:image"]', { name: "twitter:image", content: imageUrl });
    } else {
      removeMeta('meta[property="og:image"]');
      removeMeta('meta[name="twitter:image"]');
    }

    if (type === "article" && publishedAt) {
      setMeta('meta[property="article:published_time"]', {
        property: "article:published_time",
        content: publishedAt,
      });
    } else {
      removeMeta('meta[property="article:published_time"]');
    }

    setStructuredData(structuredData);
  }, [description, image, noindex, path, publishedAt, structuredData, title, type]);

  return null;
}

export function withBrand(title) {
  const cleanedTitle = cleanText(title);
  return cleanedTitle.endsWith(`| ${SITE_NAME}`) ? cleanedTitle : `${cleanedTitle} | ${SITE_NAME}`;
}
