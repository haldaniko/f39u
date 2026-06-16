import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { fetchAdminArticles, fetchAdminStatistics } from "../../services/adminService";
import StatusBadge from "../components/StatusBadge";

const cards = [
  { key: "total_articles", label: "All articles", tone: "text-slate-950 dark:text-white" },
  { key: "published_articles", label: "Published", tone: "text-emerald-700 dark:text-emerald-300" },
  { key: "pending_moderation", label: "Pending review", tone: "text-amber-700 dark:text-amber-300" },
  { key: "rejected_articles", label: "Rejected", tone: "text-red-700 dark:text-red-300" },
];

function shortDate(value) {
  return value ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value)) : "Not published";
}

export default function AdminDashboard() {
  const stats = useQuery({ queryKey: ["admin", "statistics"], queryFn: fetchAdminStatistics });
  const recent = useQuery({
    queryKey: ["admin", "articles", "recent"],
    queryFn: () => fetchAdminArticles({ page: 1, ordering: "-updated_at" }),
  });

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-teal-700 dark:text-teal-300">Editorial overview</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Good to see you.</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">A quick look at the current publishing queue.</p>
        </div>
        <Link to="/admin/articles/new" className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-700 dark:bg-teal-400 dark:text-slate-950">
          Create article
        </Link>
      </div>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <div key={card.key} className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <p className="text-sm text-slate-500 dark:text-slate-400">{card.label}</p>
            <p className={`mt-3 text-3xl font-semibold ${card.tone}`}>{stats.data?.[card.key] ?? "-"}</p>
          </div>
        ))}
      </section>

      <section className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
          <div>
            <h2 className="font-semibold">Recently updated</h2>
            <p className="mt-1 text-xs text-slate-500">Latest editorial activity</p>
          </div>
          <Link to="/admin/articles" className="text-sm font-medium text-teal-700 dark:text-teal-300">View all</Link>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {(recent.data?.results || []).slice(0, 6).map((article) => (
            <Link key={article.id} to={`/admin/articles/${article.id}/edit`} className="grid gap-2 px-5 py-4 hover:bg-slate-50 sm:grid-cols-[1fr_auto_auto] sm:items-center sm:gap-5 dark:hover:bg-slate-800/50">
              <div className="min-w-0">
                <p className="truncate font-medium">{article.title}</p>
                <p className="mt-1 truncate text-xs text-slate-500">{article.category?.name || "Uncategorized"}</p>
              </div>
              <StatusBadge status={article.status} />
              <span className="text-xs text-slate-500">{shortDate(article.updated_at)}</span>
            </Link>
          ))}
          {!recent.isLoading && !recent.data?.results?.length && <p className="px-5 py-10 text-center text-sm text-slate-500">No articles yet.</p>}
        </div>
      </section>
    </div>
  );
}
