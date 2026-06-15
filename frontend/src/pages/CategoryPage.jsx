import { useMemo } from "react";
import { useParams } from "react-router-dom";

import ArticleCard from "../components/ArticleCard";
import Seo, { withBrand } from "../components/Seo";
import { useCategories, useInfiniteNews } from "../hooks/useNewsQuery";

export default function CategoryPage() {
  const { slug } = useParams();
  const newsQuery = useInfiniteNews();
  const categoriesQuery = useCategories();
  const all = newsQuery.data?.pages.flatMap((page) => page.results || []) || [];
  const categories = categoriesQuery.data || [];
  const category = categories.find((item) => item.slug === slug);
  const categoryName = category?.name || slug.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
  const description = category?.description || `Latest ${categoryName} news, stories and developments curated by FXLFM.`;

  const filtered = useMemo(
    () => all.filter((article) => article.category?.slug === slug || article.category?.name?.toLowerCase() === slug),
    [all, slug]
  );

  return (
    <section>
      <Seo title={withBrand(`${categoryName} News`)} description={description} path={`/category/${slug}`} />
      <h1 className="font-display text-4xl capitalize">{categoryName} News</h1>
      <p className="text-slate-600 dark:text-slate-300 mt-2">{description}</p>
      <div className="news-grid mt-8">
        {filtered.map((article, i) => (
          <ArticleCard key={article.slug} article={article} index={i} />
        ))}
      </div>
      {!filtered.length && <p className="mt-8">No published stories yet for this section.</p>}
    </section>
  );
}
