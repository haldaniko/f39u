import { useState } from "react";
import { Link } from "react-router-dom";

import PageSkeleton from "../components/PageSkeleton";
import { useSearch } from "../hooks/useNewsQuery";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const { data, isLoading } = useSearch(query);

  return (
    <section className="max-w-4xl mx-auto">
      <h1 className="font-display text-4xl">Search Stories</h1>
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search by title or content"
        className="mt-4 w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-4 py-3"
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
    </section>
  );
}
