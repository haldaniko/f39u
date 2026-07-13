import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { deleteAdminArticle, fetchAdminArticle, updateAdminArticle } from "../../services/adminService";
import StatusBadge from "../components/StatusBadge";

function formatDate(value) {
  if (!value) return "Не указано";
  return new Intl.DateTimeFormat("ru", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function renderParagraphs(content) {
  const paragraphs = (content || "").split(/\n\s*\n/).map((item) => item.trim()).filter(Boolean);
  if (!paragraphs.length) {
    return <p className="text-slate-500">Текст статьи пока не заполнен.</p>;
  }
  return paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>);
}

export default function AdminArticleView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const article = useQuery({
    queryKey: ["admin", "article", id],
    queryFn: () => fetchAdminArticle(id),
  });

  const saveStatus = useMutation({
    mutationFn: (status) => updateAdminArticle(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin"] });
    },
  });

  const removeArticle = useMutation({
    mutationFn: deleteAdminArticle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin"] });
      navigate("/admin/articles", { replace: true });
    },
  });

  const handleDelete = () => {
    if (window.confirm(`Удалить "${article.data?.title}"? Это действие нельзя отменить.`)) {
      removeArticle.mutate(id);
    }
  };

  if (article.isLoading) return <p className="py-16 text-center text-sm text-slate-500">Загружаем статью...</p>;
  if (article.isError) return <p className="py-16 text-center text-sm text-red-600">{article.error.message}</p>;

  const data = article.data;

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <Link to="/admin/articles" className="text-sm font-medium text-teal-700 dark:text-teal-300">Назад к контенту</Link>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <StatusBadge status={data.status} />
            <span className="text-sm text-slate-500">Обновлено: {formatDate(data.updated_at)}</span>
          </div>
          <h1 className="mt-3 max-w-4xl text-3xl font-semibold tracking-tight">{data.title}</h1>
          <p className="mt-2 text-sm text-slate-500">/article/{data.slug}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {data.status === "published" && (
            <a href={`/article/${data.slug}`} target="_blank" rel="noreferrer" className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-medium hover:border-teal-600 dark:border-slate-700">
              На сайте
            </a>
          )}
          <Link to={`/admin/articles/${data.id}/edit`} className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-700 dark:bg-teal-400 dark:text-slate-950">
            Редактировать
          </Link>
        </div>
      </div>

      <div className="mt-7 grid gap-6 xl:grid-cols-[minmax(0,1fr)_330px]">
        <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          {data.image_url && <img src={data.image_url} alt="" className="h-72 w-full object-cover" />}
          <div className="p-6 sm:p-8">
            <p className="text-xs uppercase tracking-[0.2em] text-teal-700 dark:text-teal-300">{data.source_name || "FXLFM Editorial"}</p>
            {data.summary && <p className="mt-4 text-xl leading-8 text-slate-600 dark:text-slate-300">{data.summary}</p>}
            <div className="mt-8 space-y-5 font-body text-base leading-8 text-slate-800 dark:text-slate-100">
              {renderParagraphs(data.rewritten_content)}
            </div>
          </div>
        </article>

        <aside className="space-y-5 self-start xl:sticky xl:top-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <h2 className="font-semibold">Публикация</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Дата публикации</dt>
                <dd className="mt-1 font-medium">{formatDate(data.published_at)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Категория</dt>
                <dd className="mt-1 font-medium">{data.category?.name || "Без категории"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Автор</dt>
                <dd className="mt-1 font-medium">{data.author?.name || "Не выбран"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Источник</dt>
                <dd className="mt-1 break-words font-medium">{data.source_url ? <a href={data.source_url} target="_blank" rel="noreferrer" className="text-teal-700 dark:text-teal-300">{data.source_name || data.source_url}</a> : data.source_name}</dd>
              </div>
            </dl>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <h2 className="font-semibold">Теги</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {(data.tags || []).map((tag) => <span key={tag.slug} className="rounded-full bg-slate-100 px-3 py-1.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">{tag.name}</span>)}
              {!data.tags?.length && <p className="text-sm text-slate-500">Теги не выбраны.</p>}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <h2 className="font-semibold">Быстрые действия</h2>
            <div className="mt-4 grid gap-2">
              {data.status !== "published" && (
                <button type="button" disabled={saveStatus.isPending} onClick={() => saveStatus.mutate("published")} className="rounded-xl border border-teal-600 px-4 py-3 text-sm font-semibold text-teal-700 disabled:opacity-50 dark:text-teal-300">
                  Опубликовать
                </button>
              )}
              {data.status === "published" && (
                <button type="button" disabled={saveStatus.isPending} onClick={() => saveStatus.mutate("draft")} className="rounded-xl border border-slate-300 px-4 py-3 text-sm font-semibold dark:border-slate-700">
                  Вернуть в черновик
                </button>
              )}
              <button type="button" disabled={removeArticle.isPending} onClick={handleDelete} className="rounded-xl border border-red-200 px-4 py-3 text-sm font-semibold text-red-700 disabled:opacity-50 dark:border-red-500/40 dark:text-red-300">
                Удалить
              </button>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
