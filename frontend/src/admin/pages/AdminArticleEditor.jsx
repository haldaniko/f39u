import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  createAdminArticle,
  fetchAdminArticle,
  fetchAdminOptions,
  updateAdminArticle,
} from "../../services/adminService";

const emptyForm = {
  title: "",
  summary: "",
  rewritten_content: "",
  seo_description: "",
  image_url: "",
  source_name: "FXLFM Editorial",
  source_url: "",
  status: "draft",
  category_id: "",
  author_id: "",
  tag_ids: [],
  published_at: "",
};

const fieldClass = "mt-2 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/10 dark:border-slate-700 dark:bg-slate-950";

function toLocalDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

export default function AdminArticleEditor() {
  const { id } = useParams();
  const isEditing = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [showPreview, setShowPreview] = useState(false);

  const options = useQuery({ queryKey: ["admin", "options"], queryFn: fetchAdminOptions });
  const article = useQuery({
    queryKey: ["admin", "article", id],
    queryFn: () => fetchAdminArticle(id),
    enabled: isEditing,
  });

  useEffect(() => {
    if (!article.data) return;
    setForm({
      ...emptyForm,
      ...article.data,
      category_id: article.data.category_id || "",
      author_id: article.data.author_id || "",
      tag_ids: article.data.tag_ids || [],
      published_at: toLocalDateTime(article.data.published_at),
    });
  }, [article.data]);

  const saveArticle = useMutation({
    mutationFn: ({ payload }) => isEditing ? updateAdminArticle(id, payload) : createAdminArticle(payload),
    onSuccess: (savedArticle) => {
      queryClient.invalidateQueries({ queryKey: ["admin"] });
      navigate(`/admin/articles/${savedArticle.id}/edit`, { replace: true });
    },
    onError: (saveError) => setError(saveError.message),
  });

  const payload = useMemo(() => ({
    ...form,
    category_id: form.category_id ? Number(form.category_id) : null,
    author_id: form.author_id ? Number(form.author_id) : null,
    tag_ids: form.tag_ids.map(Number),
    published_at: form.published_at ? new Date(form.published_at).toISOString() : null,
  }), [form]);

  const submit = (event, statusOverride) => {
    event?.preventDefault();
    setError("");
    if (!form.title.trim() || !form.rewritten_content.trim()) {
      setError("Title and article content are required.");
      return;
    }
    saveArticle.mutate({ payload: { ...payload, ...(statusOverride ? { status: statusOverride } : {}) } });
  };

  const toggleTag = (tagId) => {
    setForm((current) => ({
      ...current,
      tag_ids: current.tag_ids.includes(tagId)
        ? current.tag_ids.filter((idValue) => idValue !== tagId)
        : [...current.tag_ids, tagId],
    }));
  };

  if (isEditing && article.isLoading) return <p className="py-16 text-center text-sm text-slate-500">Loading article...</p>;

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Link to="/admin/articles" className="text-sm font-medium text-teal-700 dark:text-teal-300">← Back to articles</Link>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">{isEditing ? "Edit article" : "Create article"}</h1>
          {article.data?.slug && <p className="mt-2 text-sm text-slate-500">/article/{article.data.slug}</p>}
        </div>
        <button type="button" onClick={() => setShowPreview(!showPreview)} className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700">
          {showPreview ? "Close preview" : "Preview"}
        </button>
      </div>

      <form onSubmit={submit} className={`mt-7 grid gap-6 ${showPreview ? "xl:grid-cols-2" : "xl:grid-cols-[minmax(0,1fr)_330px]"}`}>
        <div className="space-y-5">
          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <label className="block text-sm font-medium">Headline
              <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} maxLength={300} className={`${fieldClass} text-base font-semibold`} placeholder="A clear, specific news headline" required />
            </label>
            <div className="mt-5 grid gap-5 md:grid-cols-2">
              <label className="block text-sm font-medium">Summary
                <textarea value={form.summary} onChange={(event) => setForm({ ...form, summary: event.target.value })} rows={5} className={fieldClass} placeholder="A short introduction shown in article cards" />
              </label>
              <label className="block text-sm font-medium">SEO description
                <textarea value={form.seo_description} onChange={(event) => setForm({ ...form, seo_description: event.target.value })} maxLength={320} rows={5} className={fieldClass} placeholder="About 150-160 characters for search results" />
                <span className="mt-1 block text-right text-xs text-slate-400">{form.seo_description.length}/320</span>
              </label>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <label className="block text-sm font-medium">Article content
              <textarea value={form.rewritten_content} onChange={(event) => setForm({ ...form, rewritten_content: event.target.value })} rows={22} className={`${fieldClass} font-body text-base leading-7`} placeholder="Write the full story here. Separate paragraphs with a blank line." required />
            </label>
          </section>

          {!showPreview && (
            <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="font-semibold">Media and source</h2>
              <div className="mt-4 grid gap-5 md:grid-cols-2">
                <label className="block text-sm font-medium md:col-span-2">Image URL
                  <input type="url" value={form.image_url} onChange={(event) => setForm({ ...form, image_url: event.target.value })} className={fieldClass} placeholder="https://..." />
                </label>
                <label className="block text-sm font-medium">Source name
                  <input value={form.source_name} onChange={(event) => setForm({ ...form, source_name: event.target.value })} className={fieldClass} />
                </label>
                <label className="block text-sm font-medium">Source URL
                  <input type="url" value={form.source_url} onChange={(event) => setForm({ ...form, source_url: event.target.value })} className={fieldClass} placeholder="Optional for original reporting" />
                </label>
              </div>
            </section>
          )}
        </div>

        {showPreview ? (
          <aside className="self-start rounded-2xl border border-slate-200 bg-white p-6 xl:sticky xl:top-6 dark:border-slate-800 dark:bg-slate-900">
            {form.image_url && <img src={form.image_url} alt="" className="h-56 w-full rounded-xl object-cover" />}
            <p className="mt-5 text-xs uppercase tracking-[0.2em] text-teal-700 dark:text-teal-300">{form.source_name || "FXLFM Editorial"}</p>
            <h2 className="mt-2 font-display text-3xl">{form.title || "Article headline"}</h2>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-300">{form.summary || "The article summary will appear here."}</p>
            <div className="mt-6 font-body leading-7 text-slate-700 dark:text-slate-200">
              {(form.rewritten_content || "Start writing to see the article preview.").split(/\n\s*\n/).map((paragraph, index) => <p key={index} className="mb-4">{paragraph}</p>)}
            </div>
          </aside>
        ) : (
          <aside className="space-y-5 self-start xl:sticky xl:top-6">
            <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="font-semibold">Publishing</h2>
              <label className="mt-4 block text-sm font-medium">Status
                <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} className={fieldClass}>
                  {(options.data?.statuses || []).map((status) => <option key={status.value} value={status.value}>{status.label}</option>)}
                </select>
              </label>
              <label className="mt-4 block text-sm font-medium">Publication date
                <input type="datetime-local" value={form.published_at} onChange={(event) => setForm({ ...form, published_at: event.target.value })} className={fieldClass} />
              </label>
              <label className="mt-4 block text-sm font-medium">Category
                <select value={form.category_id} onChange={(event) => setForm({ ...form, category_id: event.target.value })} className={fieldClass}>
                  <option value="">Uncategorized</option>
                  {(options.data?.categories || []).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                </select>
              </label>
              <label className="mt-4 block text-sm font-medium">Author
                <select value={form.author_id} onChange={(event) => setForm({ ...form, author_id: event.target.value })} className={fieldClass}>
                  <option value="">No author</option>
                  {(options.data?.authors || []).map((author) => <option key={author.id} value={author.id}>{author.name}</option>)}
                </select>
              </label>
            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="font-semibold">Tags</h2>
              <div className="mt-3 flex max-h-48 flex-wrap gap-2 overflow-y-auto">
                {(options.data?.tags || []).map((tag) => {
                  const selected = form.tag_ids.includes(tag.id);
                  return <button key={tag.id} type="button" onClick={() => toggleTag(tag.id)} className={`rounded-full px-3 py-1.5 text-xs ${selected ? "bg-teal-600 text-white" : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"}`}>{tag.name}</button>;
                })}
                {!options.data?.tags?.length && <p className="text-xs text-slate-500">No tags available.</p>}
              </div>
            </section>

            {error && <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-300">{error}</p>}
            <div className="grid gap-2">
              <button type="submit" disabled={saveArticle.isPending} className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50 dark:bg-teal-400 dark:text-slate-950">
                {saveArticle.isPending ? "Saving..." : "Save changes"}
              </button>
              {form.status !== "published" && <button type="button" disabled={saveArticle.isPending} onClick={(event) => submit(event, "published")} className="rounded-xl border border-teal-600 px-4 py-3 text-sm font-semibold text-teal-700 dark:text-teal-300">Publish now</button>}
            </div>
          </aside>
        )}
      </form>
    </div>
  );
}
