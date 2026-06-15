import { Link, useParams } from "react-router-dom";

import PageSkeleton from "../components/PageSkeleton";
import Seo, { withBrand } from "../components/Seo";
import { useArticle, useTrending } from "../hooks/useNewsQuery";
import { estimateReadingTime, formatDate } from "../utils/formatters";

export default function ArticlePage() {
  const { slug } = useParams();
  const { data: article, isLoading } = useArticle(slug);
  const { data: related = [] } = useTrending();

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

  return (
    <>
      <Seo
        title={withBrand(article.title)}
        description={article.seo_description || article.summary}
        path={`/article/${article.slug}`}
        image={article.image_url}
        type="article"
        publishedAt={article.published_at}
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
          <span>{formatDate(article.published_at)}</span>
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
            {related.slice(0, 4).map((item) => (
              <Link key={item.slug} to={`/article/${item.slug}`} className="glass rounded-xl p-3 hover:shadow-lg">
                <p className="font-display text-lg">{item.title}</p>
              </Link>
            ))}
          </div>
        </section>
      </article>
    </>
  );
}
