import { Link, useParams } from "react-router-dom";

import PageSkeleton from "../components/PageSkeleton";
import Seo, { absoluteUrl, withBrand } from "../components/Seo";
import { useArticle, useRelatedStories } from "../hooks/useNewsQuery";
import { estimateReadingTime, formatDate } from "../utils/formatters";

export default function ArticlePage() {
  const { slug } = useParams();
  const { data: article, isLoading } = useArticle(slug);
  const { data: related = [] } = useRelatedStories(slug);

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
        <p>Article not found.</p>
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
      <article className="max-w-4xl mx-auto">
        <img
          src={article.image_url || "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1600&q=80"}
          alt={article.title}
          className="w-full h-64 md:h-96 object-cover rounded-3xl"
        />
        <p className="font-ui mt-5 text-xs uppercase tracking-[0.24em] text-brand-700 dark:text-brand-300">{article.source_name}</p>
        <h1 className="font-display text-4xl md:text-5xl mt-3">{article.title}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-300 font-ui">
          {author ? <Link to={`/author/${author.slug}`}>By {author.name}</Link> : <span>By Future Xclusive News</span>}
          <span>{formatDate(publicationDate)}</span>
          <span>{estimateReadingTime(article.rewritten_content)}</span>
        </div>
        <p className="mt-4 text-xl text-slate-700 dark:text-slate-300">{article.summary}</p>
        <div className="prose prose-slate dark:prose-invert max-w-none mt-8">
          {article.rewritten_content?.split("\n").map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </div>
        <div className="mt-6 flex flex-wrap gap-2">
          {(article.tags || []).map((tag) => (
            <span key={tag.slug} className="text-xs glass rounded-full px-3 py-1">#{tag.name}</span>
          ))}
        </div>
        <div className="mt-8 flex gap-3">
          <a href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title)}`} className="glass px-4 py-2 rounded-full text-sm">Share X</a>
          <a href={`mailto:?subject=${encodeURIComponent(article.title)}&body=${encodeURIComponent(window.location.href)}`} className="glass px-4 py-2 rounded-full text-sm">Email</a>
        </div>

        <section className="mt-12">
          <h2 className="font-display text-2xl">Related Stories</h2>
          <div className="mt-4 grid md:grid-cols-2 gap-3">
            {related.map((item) => (
              <Link key={item.slug} to={`/article/${item.slug}`} className="glass rounded-xl p-4 hover:shadow-lg">
                {item.category?.name && (
                  <p className="font-ui text-xs uppercase tracking-[0.18em] text-brand-700 dark:text-brand-300">
                    {item.category.name}
                  </p>
                )}
                <p className="font-display text-lg mt-1">{item.title}</p>
                {item.summary && <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{item.summary}</p>}
              </Link>
            ))}
          </div>
        </section>
      </article>
    </>
  );
}
