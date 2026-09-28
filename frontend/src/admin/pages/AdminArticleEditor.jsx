import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  createAdminArticle,
  fetchAdminArticle,
  fetchAdminOptions,
  updateAdminArticle,
} from "../../services/adminService";
import { formatStatus } from "../components/StatusBadge";

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
  category_ids: [],
  author_id: "",
  tag_names: [],
  published_at: "",
};

const fieldClass = "mt-2 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/10 dark:border-slate-700 dark:bg-slate-950";

function toLocalDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function normalizeIds(values = []) {
  return values.map((value) => Number(value)).filter(Boolean);
}

export default function AdminArticleEditor() {
  const { id } = useParams();
  const isEditing = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [tagInput, setTagInput] = useState("");

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
      category_ids: normalizeIds(article.data.category_ids || article.data.categories?.map((category) => category.id) || (article.data.category_id ? [article.data.category_id] : [])),
      author_id: article.data.author_id || "",
      tag_names: article.data.tags?.map((tag) => tag.name) || [],
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
    category_id: form.category_ids[0] || (form.category_id ? Number(form.category_id) : null),
    category_ids: normalizeIds(form.category_ids),
    author_id: form.author_id ? Number(form.author_id) : null,
    tag_names: form.tag_names,
    published_at: form.published_at ? new Date(form.published_at).toISOString() : null,
  }), [form]);

  const submit = (event, statusOverride) => {
    event?.preventDefault();
    setError("");
    if (!form.title.trim() || !form.rewritten_content.trim()) {
      setError("Enter an article title and content.");
      return;
    }
    const pendingTag = tagInput.trim().replace(/^#+/, "").trim();
    const tagNames = pendingTag && !form.tag_names.some((tag) => tag.toLowerCase() === pendingTag.toLowerCase())
      ? [...form.tag_names, pendingTag]
      : form.tag_names;
    saveArticle.mutate({ payload: { ...payload, tag_names: tagNames, ...(statusOverride ? { status: statusOverride } : {}) } });
  };

  const addTag = (rawValue) => {
    const name = rawValue.trim().replace(/^#+/, "").trim();
    if (!name) return;
    setForm((current) => ({
      ...current,
      tag_names: current.tag_names.some((tag) => tag.toLowerCase() === name.toLowerCase())
        ? current.tag_names
        : [...current.tag_names, name],
    }));
    setTagInput("");
  };

  const handleTagKeyDown = (event) => {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      addTag(tagInput);
    }
    if (event.key === "Backspace" && !tagInput && form.tag_names.length) {
      setForm((current) => ({ ...current, tag_names: current.tag_names.slice(0, -1) }));
    }
  };

  if (isEditing && article.isLoading) return <p className="py-16 text-center text-sm text-slate-500">Loading article...</p>;

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Link to="/admin/articles" className="text-sm font-medium text-teal-700 dark:text-teal-300">Back to articles</Link>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">{isEditing ? "Edit article" : "New article"}</h1>
          {article.data?.slug && <p className="mt-2 text-sm text-slate-500">/article/{article.data.slug}</p>}
        </div>
        <div className="flex flex-wrap gap-2">
          {isEditing && <Link to={`/admin/articles/${id}`} className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700">View</Link>}
          <button type="button" onClick={() => setShowPreview(!showPreview)} className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700">
            {showPreview ? "Close preview" : "Preview"}
          </button>
        </div>
      </div>

      <form onSubmit={submit} className={`mt-7 grid gap-6 ${showPreview ? "xl:grid-cols-2" : "xl:grid-cols-[minmax(0,1fr)_330px]"}`}>
        <div className="space-y-5">
          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <label className="block text-sm font-medium">Title
              <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} maxLength={300} className={`${fieldClass} text-base font-semibold`} placeholder="A clear and concise headline" required />
            </label>
            <div className="mt-5 grid gap-5 md:grid-cols-2">
              <label className="block text-sm font-medium">Summary
                <textarea value={form.summary} onChange={(event) => setForm({ ...form, summary: event.target.value })} rows={5} className={fieldClass} placeholder="A short lead shown on cards and at the beginning of the article" />
              </label>
              <label className="block text-sm font-medium">SEO description
                <textarea value={form.seo_description} onChange={(event) => setForm({ ...form, seo_description: event.target.value })} maxLength={320} rows={5} className={fieldClass} placeholder="Description for search engines" />
                <span className="mt-1 block text-right text-xs text-slate-400">{form.seo_description.length}/320</span>
              </label>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <label className="block text-sm font-medium">Article content
              <textarea value={form.rewritten_content} onChange={(event) => setForm({ ...form, rewritten_content: event.target.value })} rows={22} className={`${fieldClass} font-body text-base leading-7`} placeholder="Write the full article here. Separate paragraphs with an empty line." required />
            </label>
          </section>

          {!showPreview && (
            <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="font-semibold">Media and source</h2>
              <div className="mt-4 grid gap-5 md:grid-cols-2">
                <label className="block text-sm font-medium md:col-span-2">Image URL
                  <input type="url" value={form.image_url} onChange={(event) => setForm({ ...form, image_url: event.target.value })} className={fieldClass} placeholder="https://..." />
                </label>
                <label className="block text-sm font-medium">Source
                  <input value={form.source_name} onChange={(event) => setForm({ ...form, source_name: event.target.value })} className={fieldClass} placeholder="FXLFM Editorial" />
                </label>
                <label className="block text-sm font-medium">Source URL
                  <input type="url" value={form.source_url} onChange={(event) => setForm({ ...form, source_url: event.target.value })} className={fieldClass} placeholder="Leave empty for an original article" />
                </label>
              </div>
            </section>
          )}
        </div>

        {showPreview ? (
          <aside className="self-start rounded-2xl border border-slate-200 bg-white p-6 xl:sticky xl:top-6 dark:border-slate-800 dark:bg-slate-900">
            {form.image_url && <img src={form.image_url} alt="" className="h-56 w-full rounded-xl object-cover" />}
            <p className="mt-5 text-xs uppercase tracking-[0.2em] text-teal-700 dark:text-teal-300">{form.source_name || "FXLFM Editorial"}</p>
            <h2 className="mt-2 font-display text-3xl">{form.title || "Article title"}</h2>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-300">{form.summary || "The article summary will appear here."}</p>
            <div className="mt-6 font-body leading-7 text-slate-700 dark:text-slate-200">
              {(form.rewritten_content || "Start writing to see a preview.").split(/\n\s*\n/).map((paragraph, index) => <p key={index} className="mb-4">{paragraph}</p>)}
            </div>
          </aside>
        ) : (
          <aside className="space-y-5 self-start xl:sticky xl:top-6">
            <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="font-semibold">Publication</h2>
              <label className="mt-4 block text-sm font-medium">Status
                <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} className={fieldClass}>
                  {(options.data?.statuses || []).map((status) => <option key={status.value} value={status.value}>{formatStatus(status.value)}</option>)}
                </select>
              </label>
              <label className="mt-4 block text-sm font-medium">Publication date
                <input type="datetime-local" value={form.published_at} onChange={(event) => setForm({ ...form, published_at: event.target.value })} className={fieldClass} />
              </label>
              <label className="mt-4 block text-sm font-medium">Categories
                <select
                  multiple
                  size={Math.max((options.data?.categories || []).length + 1, 6)}
                  value={form.category_ids.map(String)}
                  onChange={(event) => setForm({ ...form, category_ids: Array.from(event.target.selectedOptions, (option) => Number(option.value)).filter(Boolean) })}
                  className={fieldClass}
                >
                  <option value="" disabled>Select one or more categories</option>
                  {(options.data?.categories || []).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                </select>
              </label>
              <label className="mt-4 block text-sm font-medium">Editor
                <select value={form.author_id} onChange={(event) => setForm({ ...form, author_id: event.target.value })} className={fieldClass}>
                  <option value="">No editor</option>
                  {(options.data?.authors || []).map((author) => <option key={author.id} value={author.id}>{author.name}</option>)}
                </select>
              </label>
            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="font-semibold">Tags</h2>
              <p className="mt-1 text-xs leading-5 text-slate-500">Enter a tag and press Enter. You can add multiple tags.</p>
              <div className="mt-3 flex min-h-12 flex-wrap items-center gap-2 rounded-lg border border-slate-300 bg-white p-2 focus-within:border-[#f4ae35] focus-within:ring-2 focus-within:ring-[#f4ae35]/20 dark:border-slate-700 dark:bg-slate-950">
                {form.tag_names.map((tag) => (
                  <span key={tag.toLowerCase()} className="inline-flex items-center gap-1.5 rounded-full bg-[#1d282d] px-3 py-1.5 text-xs font-bold text-white">
                    {tag}
                    <button
                      type="button"
                      aria-label={`Remove tag ${tag}`}
                      onClick={() => setForm((current) => ({ ...current, tag_names: current.tag_names.filter((item) => item !== tag) }))}
                      className="text-slate-400 hover:text-[#f4ae35]"
                    >
                      ×
                    </button>
                  </span>
                ))}
                <input
                  value={tagInput}
                  onChange={(event) => setTagInput(event.target.value)}
                  onKeyDown={handleTagKeyDown}
                  onBlur={() => addTag(tagInput)}
                  maxLength={80}
                  className="min-w-[130px] flex-1 bg-transparent px-1 py-1.5 text-sm outline-none"
                  placeholder={form.tag_names.length ? "Add another tag..." : "For example: Ukraine"}
                />
              </div>
            </section>

            {error && <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-300">{error}</p>}
            <div className="grid gap-2">
              <button type="submit" disabled={saveArticle.isPending} className="rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50 dark:bg-teal-400 dark:text-slate-950">
                {saveArticle.isPending ? "Saving..." : "Save"}
              </button>
              {form.status !== "published" && <button type="button" disabled={saveArticle.isPending} onClick={(event) => submit(event, "published")} className="rounded-xl border border-teal-600 px-4 py-3 text-sm font-semibold text-teal-700 dark:text-teal-300">Publish now</button>}
            </div>
          </aside>
        )}
      </form>
    </div>
  );
}
