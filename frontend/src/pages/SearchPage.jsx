import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import PageSkeleton from "../components/PageSkeleton";
import Seo, { withBrand } from "../components/Seo";
import { useSearch } from "../hooks/useNewsQuery";

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const trimmedQuery = query.trim();
  const { data, isLoading } = useSearch(trimmedQuery);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  const handleQueryChange = (event) => {
    const nextQuery = event.target.value;
    setQuery(nextQuery);

    const nextTrimmedQuery = nextQuery.trim();
    if (nextTrimmedQuery) {
      setSearchParams({ q: nextTrimmedQuery }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  };

  return (
    <section className="mx-auto max-w-4xl py-10">
      <Seo
        title={withBrand(trimmedQuery.length > 1 ? `Search Results for ${trimmedQuery}` : "Search News")}
        description="Search FXLFM for the latest global news, reporting and analysis."
        path={trimmedQuery ? `/search?q=${encodeURIComponent(trimmedQuery)}` : "/search"}
        noindex
      />
      <h1 className="font-display text-4xl">Search Stories</h1>
      <input
        value={query}
        onChange={handleQueryChange}
        placeholder="Search by title"
        className="mt-4 w-full rounded-xl border border-slate-300 bg-white/80 px-4 py-3 outline-none transition focus:border-amber-400 focus:ring-2 focus:ring-amber-400/30 dark:border-slate-700 dark:bg-slate-900/60"
      />
      {isLoading && <PageSkeleton />}
      <div className="mt-6 space-y-3">
        {(data || []).map((article) => (
          <Link key={article.slug} to={`/article/${article.slug}`} className="glass block rounded-xl p-4 hover:shadow-lg">
            <p className="font-display text-xl">{article.title}</p>
            <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">{article.summary}</p>
          </Link>
        ))}
      </div>
      {!isLoading && trimmedQuery.length > 1 && (data || []).length === 0 && (
        <p className="mt-6 rounded-xl border border-slate-200 bg-white/70 p-4 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-300">
          No articles found by this title.
        </p>
      )}
    </section>
  );
}
