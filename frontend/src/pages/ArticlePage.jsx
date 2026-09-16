import { Link, useParams } from "react-router-dom";

import {
  BackToTop,
  NewsletterBand,
  ShareLinks,
  StoryCard,
  fallbackImage,
} from "../components/DesignPrimitives";
import PageSkeleton from "../components/PageSkeleton";
import Seo, { absoluteUrl, withBrand } from "../components/Seo";
import { useArticle, useRelatedStories } from "../hooks/useNewsQuery";
import { estimateReadingTime, formatDate } from "../utils/formatters";

const fallbackRelated = Array.from({ length: 4 }, (_, index) => ({
  slug: `related-${index}`,
  title: "Art Basel brings fun back to the fair with the element of surprise",
  source_name: "Investor.bg",
  category: { name: "Art", slug: "art" },
}));

export default function ArticlePage() {
  const { slug } = useParams();
  const { data, isLoading } = useArticle(slug);
  const { data: relatedData = [] } = useRelatedStories(slug);
  const article = data && typeof data === "object" ? data : null;
  const related = Array.isArray(relatedData) && relatedData.length ? relatedData : fallbackRelated;

  if (isLoading) {
    return (
      <>
        <Seo
          title={withBrand("Latest News Story")}
          description="Read the latest global news, analysis and developments from FXLFM."
          path={`/article/${slug}`}
        />
        <PageSkeleton />
      </>
    );
  }

  if (!article) {
    return (
      <>
        <Seo
          title={withBrand("Article Not Found")}
          description="The requested FXLFM news article could not be found."
          path={`/article/${slug}`}
          noindex
        />
        <div className="py-20">
          <p>Article not found.</p>
        </div>
      </>
    );
  }

  const articleUrl = absoluteUrl(`/article/${article.slug}`);
  const publicationDate = article.published_at || article.created_at;
  const modifiedDate = article.updated_at || publicationDate;
  const author = article.author;
  const authorSocialUrls = author
    ? [author.x_url, author.linkedin_url, author.instagram_url].filter(Boolean)
    : [];
  const category = article.category?.name || "Art";
  const body = article.rewritten_content || article.summary || "";
  const paragraphs = body.split("\n").filter(Boolean);
  const newsArticleSchema = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.title,
    description: article.seo_description || article.summary || article.title,
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": articleUrl,
    },
    datePublished: publicationDate,
    dateModified: modifiedDate,
    author: author
      ? {
          "@type": "Person",
          name: author.name,
          url: absoluteUrl(`/author/${author.slug}`),
          ...(authorSocialUrls.length ? { sameAs: authorSocialUrls } : {}),
        }
      : {
          "@type": "Organization",
          name: "Future Xclusive News",
          url: absoluteUrl("/"),
        },
    publisher: {
      "@type": "Organization",
      name: "Future Xclusive News",
      url: absoluteUrl("/"),
    },
    ...(article.image_url ? { image: [absoluteUrl(article.image_url)] } : {}),
    ...(article.category?.name ? { articleSection: article.category.name } : {}),
    ...((article.tags || []).length
      ? { keywords: article.tags.map((tag) => tag.name).join(", ") }
      : {}),
  };

  return (
    <>
      <Seo
        title={withBrand(article.title)}
        description={article.seo_description || article.summary}
        path={`/article/${article.slug}`}
        image={article.image_url}
        type="article"
        publishedAt={publicationDate}
        structuredData={newsArticleSchema}
      />
      <article className="pb-4 pt-12">
        <nav className="font-ui text-sm font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          <Link to="/">Home</Link>
          <span className="mx-2">/</span>
          <Link to={`/category/${article.category?.slug || "art"}`} className="text-slate-950 dark:text-white">{category}</Link>
          <span className="mx-2 hidden sm:inline">/</span>
          <span className="hidden sm:inline">{article.title.slice(0, 34)}...</span>
        </nav>

        <h1 className="mt-14 max-w-6xl font-body text-5xl font-bold leading-tight tracking-normal md:text-7xl">
          {article.title}
        </h1>

        <div className="mt-10 flex flex-wrap items-end justify-between gap-6">
          <div className="flex items-center gap-4">
            <img
              src={author?.photo_url || "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80"}
              alt={author?.name || "Author"}
              className="h-14 w-14 rounded-full object-cover"
            />
            <div>
              <p className="font-ui text-xs text-slate-500 dark:text-slate-400">Author</p>
              <p className="font-ui text-lg font-bold">{author?.name || "Maria Nicholson"}</p>
            </div>
          </div>
          <div className="flex gap-8 font-ui text-sm font-bold uppercase text-slate-500 dark:text-slate-400">
            <span>{formatDate(publicationDate)}</span>
            <span className="text-amber-500">⌁ {category}</span>
            <span>{estimateReadingTime(body)}</span>
          </div>
        </div>

        <div className="mt-8 h-[330px] overflow-hidden">
          <img
            src={article.image_url || fallbackImage}
            alt={article.title}
            className="h-full w-full object-cover"
          />
        </div>

        <div className="mt-24 grid gap-16 lg:grid-cols-[1fr_360px]">
          <div>
            <p className="font-body text-3xl font-semibold leading-tight md:text-4xl">
              {article.summary || "Titles should have this size, font, weight and line height example: Bulgaria is the top rated country for tourism this summer."}
            </p>
            <div className="mt-12 space-y-8 font-ui text-2xl leading-relaxed text-slate-900 dark:text-slate-200">
              {(paragraphs.length ? paragraphs : [article.summary, article.summary]).filter(Boolean).map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
            <div className="mt-16 grid h-72 place-items-center rounded-lg bg-[#282524] font-ui text-sm font-semibold uppercase text-white dark:bg-white dark:text-slate-900">
              Advert
            </div>
          </div>

          <aside className="space-y-12">
            <ShareLinks />
            <section>
              <h2 className="font-ui text-xl font-bold uppercase">You may be interested</h2>
              <div className="mt-5 space-y-4">
                <StoryCard article={related[0]} />
                {related.slice(1, 4).map((item) => (
                  <StoryCard key={item.slug} article={item} variant="line" />
                ))}
              </div>
            </section>
          </aside>
        </div>
      </article>
      <NewsletterBand />
      <BackToTop />
    </>
  );
}
