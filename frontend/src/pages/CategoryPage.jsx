import { useMemo } from "react";
import { useParams } from "react-router-dom";

import ArticleCard from "../components/ArticleCard";
import { useInfiniteNews } from "../hooks/useNewsQuery";

export default function CategoryPage() {
  const { slug } = useParams();
  const newsQuery = useInfiniteNews();
  const all = newsQuery.data?.pages.flatMap((page) => page.results || []) || [];

  const filtered = useMemo(
    () => all.filter((article) => article.category?.slug === slug || article.category?.name?.toLowerCase() === slug),
    [all, slug]
  );

  return (
    <section>
      <h1 className="font-display text-4xl capitalize">{slug} News</h1>
      <p className="text-slate-600 dark:text-slate-300 mt-2">Curated stories for this category.</p>
      <div className="news-grid mt-8">
        {filtered.map((article, i) => (
          <ArticleCard key={article.slug} article={article} index={i} />
        ))}
      </div>
      {!filtered.length && <p className="mt-8">No published stories yet for this section.</p>}
    </section>
  );
}
