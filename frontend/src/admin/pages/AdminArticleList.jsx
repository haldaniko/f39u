import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { deleteAdminArticle, fetchAdminArticles, fetchAdminOptions } from "../../services/adminService";
import StatusBadge from "../components/StatusBadge";

export default function AdminArticleList() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({ search: "", status: "", page: 1 });
  const options = useQuery({ queryKey: ["admin", "options"], queryFn: fetchAdminOptions });
  const articles = useQuery({
    queryKey: ["admin", "articles", filters],
    queryFn: () => fetchAdminArticles({ ...filters, status: filters.status || undefined }),
  });
  const removeArticle = useMutation({
    mutationFn: deleteAdminArticle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "articles"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "statistics"] });
    },
  });

  const handleDelete = (article) => {
    if (window.confirm(`Delete “${article.title}”? This cannot be undone.`)) {
      removeArticle.mutate(article.id);
    }
  };

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-teal-700 dark:text-teal-300">Content library</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Articles</h1>
          <p className="mt-2 text-sm text-slate-500">Search, review and manage every story.</p>
        </div>
        <Link to="/admin/articles/new" className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-700 dark:bg-teal-400 dark:text-slate-950">New article</Link>
      </div>

      <div className="mt-7 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 sm:grid-cols-[1fr_220px] dark:border-slate-800 dark:bg-slate-900">
        <input
          type="search"
          placeholder="Search title, source or slug..."
          value={filters.search}
          onChange={(event) => setFilters({ ...filters, search: event.target.value, page: 1 })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        />
        <select
          value={filters.status}
          onChange={(event) => setFilters({ ...filters, status: event.target.value, page: 1 })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        >
          <option value="">All statuses</option>
          {(options.data?.statuses || []).map((status) => <option key={status.value} value={status.value}>{status.label}</option>)}
        </select>
      </div>

      <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <table className="w-full min-w-[850px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:border-slate-800 dark:bg-slate-900">
            <tr><th className="px-5 py-3">Story</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Category</th><th className="px-4 py-3">Updated</th><th className="px-5 py-3 text-right">Actions</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {(articles.data?.results || []).map((article) => (
              <tr key={article.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                <td className="max-w-lg px-5 py-4"><p className="truncate font-medium">{article.title}</p><p className="mt-1 truncate text-xs text-slate-500">/{article.slug}</p></td>
                <td className="px-4 py-4"><StatusBadge status={article.status} /></td>
                <td className="px-4 py-4 text-slate-600 dark:text-slate-300">{article.category?.name || "-"}</td>
                <td className="px-4 py-4 text-xs text-slate-500">{new Date(article.updated_at).toLocaleDateString()}</td>
                <td className="px-5 py-4 text-right whitespace-nowrap">
                  {article.status === "published" && <a href={`/article/${article.slug}`} target="_blank" rel="noreferrer" className="mr-3 text-slate-500 hover:text-teal-700">View</a>}
                  <Link to={`/admin/articles/${article.id}/edit`} className="mr-3 font-medium text-teal-700 dark:text-teal-300">Edit</Link>
                  <button type="button" onClick={() => handleDelete(article)} className="text-red-600 hover:text-red-800">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {articles.isLoading && <p className="px-5 py-12 text-center text-sm text-slate-500">Loading articles...</p>}
        {!articles.isLoading && !articles.data?.results?.length && <p className="px-5 py-12 text-center text-sm text-slate-500">No articles match these filters.</p>}
      </div>

      <div className="mt-4 flex items-center justify-between text-sm">
        <span className="text-slate-500">{articles.data?.count ?? 0} articles</span>
        <div className="flex gap-2">
          <button disabled={!articles.data?.previous} onClick={() => setFilters({ ...filters, page: filters.page - 1 })} className="rounded-lg border border-slate-300 px-3 py-2 disabled:opacity-40 dark:border-slate-700">Previous</button>
          <span className="px-2 py-2">Page {filters.page}</span>
          <button disabled={!articles.data?.next} onClick={() => setFilters({ ...filters, page: filters.page + 1 })} className="rounded-lg border border-slate-300 px-3 py-2 disabled:opacity-40 dark:border-slate-700">Next</button>
        </div>
      </div>
    </div>
  );
}
