import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { deleteAdminArticle, fetchAdminArticles, fetchAdminOptions } from "../../services/adminService";
import StatusBadge, { formatStatus } from "../components/StatusBadge";

const orderingOptions = [
  { value: "-updated_at", label: "Сначала обновленные" },
  { value: "-created_at", label: "Сначала новые" },
  { value: "-published_at", label: "Сначала опубликованные" },
  { value: "title", label: "По заголовку" },
];

export default function AdminArticleList() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    search: "",
    status: "",
    category: "",
    author: "",
    ordering: "-updated_at",
    page: 1,
  });
  const options = useQuery({ queryKey: ["admin", "options"], queryFn: fetchAdminOptions });
  const articles = useQuery({
    queryKey: ["admin", "articles", filters],
    queryFn: () => fetchAdminArticles({
      ...filters,
      status: filters.status || undefined,
      category: filters.category || undefined,
      author: filters.author || undefined,
    }),
  });
  const removeArticle = useMutation({
    mutationFn: deleteAdminArticle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "articles"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "statistics"] });
    },
  });

  const patchFilters = (nextFilters) => setFilters((current) => ({ ...current, ...nextFilters, page: 1 }));

  const handleDelete = (article) => {
    if (window.confirm(`Удалить "${article.title}"? Это действие нельзя отменить.`)) {
      removeArticle.mutate(article.id);
    }
  };

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-teal-700 dark:text-teal-300">Библиотека контента</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Статьи</h1>
          <p className="mt-2 text-sm text-slate-500">Просматривайте, фильтруйте и управляйте всеми материалами.</p>
        </div>
        <Link to="/admin/articles/new" className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-700 dark:bg-teal-400 dark:text-slate-950">Добавить статью</Link>
      </div>

      <div className="mt-7 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 md:grid-cols-2 xl:grid-cols-[minmax(260px,1fr)_180px_210px_210px_210px] dark:border-slate-800 dark:bg-slate-900">
        <input
          type="search"
          placeholder="Поиск по заголовку, источнику или slug..."
          value={filters.search}
          onChange={(event) => patchFilters({ search: event.target.value })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        />
        <select
          value={filters.status}
          onChange={(event) => patchFilters({ status: event.target.value })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        >
          <option value="">Все статусы</option>
          {(options.data?.statuses || []).map((status) => <option key={status.value} value={status.value}>{formatStatus(status.value)}</option>)}
        </select>
        <select
          value={filters.category}
          onChange={(event) => patchFilters({ category: event.target.value })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        >
          <option value="">Все категории</option>
          {(options.data?.categories || []).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select>
        <select
          value={filters.author}
          onChange={(event) => patchFilters({ author: event.target.value })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        >
          <option value="">Все авторы</option>
          {(options.data?.authors || []).map((author) => <option key={author.id} value={author.id}>{author.name}</option>)}
        </select>
        <select
          value={filters.ordering}
          onChange={(event) => patchFilters({ ordering: event.target.value })}
          className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-950"
        >
          {orderingOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>

      <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <table className="w-full min-w-[850px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:border-slate-800 dark:bg-slate-900">
            <tr><th className="px-5 py-3">Материал</th><th className="px-4 py-3">Статус</th><th className="px-4 py-3">Категория</th><th className="px-4 py-3">Обновлено</th><th className="px-5 py-3 text-right">Действия</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {(articles.data?.results || []).map((article) => (
              <tr key={article.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                <td className="max-w-lg px-5 py-4"><Link to={`/admin/articles/${article.id}`} className="block truncate font-medium hover:text-teal-700 dark:hover:text-teal-300">{article.title}</Link><p className="mt-1 truncate text-xs text-slate-500">/{article.slug}</p></td>
                <td className="px-4 py-4"><StatusBadge status={article.status} /></td>
                <td className="px-4 py-4 text-slate-600 dark:text-slate-300">{article.category?.name || "-"}</td>
                <td className="px-4 py-4 text-xs text-slate-500">{new Date(article.updated_at).toLocaleDateString("ru")}</td>
                <td className="px-5 py-4 text-right whitespace-nowrap">
                  <Link to={`/admin/articles/${article.id}`} className="mr-3 text-slate-500 hover:text-teal-700">Смотреть</Link>
                  <Link to={`/admin/articles/${article.id}/edit`} className="mr-3 font-medium text-teal-700 dark:text-teal-300">Править</Link>
                  <button type="button" onClick={() => handleDelete(article)} className="text-red-600 hover:text-red-800">Удалить</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {articles.isLoading && <p className="px-5 py-12 text-center text-sm text-slate-500">Загружаем статьи...</p>}
        {!articles.isLoading && !articles.data?.results?.length && <p className="px-5 py-12 text-center text-sm text-slate-500">Под эти фильтры ничего не найдено.</p>}
      </div>

      <div className="mt-4 flex items-center justify-between text-sm">
        <span className="text-slate-500">Материалов: {articles.data?.count ?? 0}</span>
        <div className="flex gap-2">
          <button disabled={!articles.data?.previous} onClick={() => setFilters({ ...filters, page: filters.page - 1 })} className="rounded-lg border border-slate-300 px-3 py-2 disabled:opacity-40 dark:border-slate-700">Назад</button>
          <span className="px-2 py-2">Страница {filters.page}</span>
          <button disabled={!articles.data?.next} onClick={() => setFilters({ ...filters, page: filters.page + 1 })} className="rounded-lg border border-slate-300 px-3 py-2 disabled:opacity-40 dark:border-slate-700">Дальше</button>
        </div>
      </div>
    </div>
  );
}
