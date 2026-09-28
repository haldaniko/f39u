import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  createAdminEditor,
  fetchAdminEditor,
  updateAdminEditor,
} from "../../services/adminService";

const emptyForm = {
  name: "",
  job_title: "",
  bio: "",
  location: "",
  x_url: "",
  linkedin_url: "",
  instagram_url: "",
  joined_at: "",
};

export default function AdminEditorEditor() {
  const { id } = useParams();
  const isEditing = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form, setForm] = useState(emptyForm);
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState("");
  const [removePhoto, setRemovePhoto] = useState(false);
  const [error, setError] = useState("");
  const editor = useQuery({
    queryKey: ["admin", "editor", id],
    queryFn: () => fetchAdminEditor(id),
    enabled: isEditing,
  });

  useEffect(() => {
    if (!editor.data) return;
    setForm({
      name: editor.data.name || "",
      job_title: editor.data.job_title || "",
      bio: editor.data.bio || "",
      location: editor.data.location || "",
      x_url: editor.data.x_url || "",
      linkedin_url: editor.data.linkedin_url || "",
      instagram_url: editor.data.instagram_url || "",
      joined_at: editor.data.joined_at || "",
    });
    setPhotoPreview(editor.data.photo_url || "");
  }, [editor.data]);

  useEffect(() => () => {
    if (photoPreview.startsWith("blob:")) URL.revokeObjectURL(photoPreview);
  }, [photoPreview]);

  const saveEditor = useMutation({
    mutationFn: (payload) => isEditing ? updateAdminEditor(id, payload) : createAdminEditor(payload),
    onSuccess: (savedEditor) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "editors"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "options"] });
      navigate(`/admin/editors/${savedEditor.id}/edit`, { replace: true });
    },
    onError: (saveError) => setError(saveError.message),
  });

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }));
  const selectPhoto = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setPhotoFile(file);
    setPhotoPreview(URL.createObjectURL(file));
    setRemovePhoto(false);
  };

  const clearPhoto = () => {
    setPhotoFile(null);
    setPhotoPreview("");
    setRemovePhoto(true);
  };

  const submit = (event) => {
    event.preventDefault();
    setError("");
    const payload = new FormData();
    Object.entries(form).forEach(([key, value]) => {
      if (key !== "joined_at" || value) payload.append(key, value);
    });
    if (photoFile) payload.append("photo", photoFile);
    if (removePhoto) payload.append("remove_photo", "true");
    saveEditor.mutate(payload);
  };

  if (isEditing && editor.isLoading) return <p className="py-16 text-center text-sm text-slate-500">Loading editor...</p>;

  return (
    <div className="mx-auto max-w-5xl">
      <Link to="/admin/editors" className="admin-link">Back to editors</Link>
      <div className="mt-2">
        <p className="admin-kicker">FXLFM team</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">{isEditing ? "Edit editor profile" : "New editor"}</h1>
      </div>

      <form onSubmit={submit} className="mt-7 grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="admin-card space-y-5 p-6">
          <div className="grid gap-5 sm:grid-cols-2">
            <label className="admin-label sm:col-span-2">Full name
              <input value={form.name} onChange={(event) => updateField("name", event.target.value)} className="admin-input mt-2" maxLength={120} required />
            </label>
            <label className="admin-label">Role
              <input value={form.job_title} onChange={(event) => updateField("job_title", event.target.value)} className="admin-input mt-2" maxLength={160} placeholder="Managing Editor" />
            </label>
            <label className="admin-label">Location
              <input value={form.location} onChange={(event) => updateField("location", event.target.value)} className="admin-input mt-2" maxLength={160} />
            </label>
            <label className="admin-label">Joined date
              <input type="date" value={form.joined_at} onChange={(event) => updateField("joined_at", event.target.value)} className="admin-input mt-2" />
            </label>
            <div className="admin-label">
              Photo
              <label className="mt-2 flex h-[42px] cursor-pointer items-center justify-between gap-3 rounded-lg border border-dashed border-slate-400 bg-slate-50 px-3 text-left transition hover:border-[#f4ae35] hover:bg-amber-50/50 dark:bg-slate-900">
                <span className="min-w-0 truncate text-sm font-bold text-slate-700 dark:text-slate-200">
                  {photoFile ? photoFile.name : "Choose photo"}
                </span>
                <span className="shrink-0 text-[10px] font-normal text-slate-500">JPG, PNG, WebP · up to 5 MB</span>
                <input type="file" accept="image/jpeg,image/png,image/webp" onChange={selectPhoto} className="sr-only" />
              </label>
            </div>
            <label className="admin-label sm:col-span-2">Biography
              <textarea value={form.bio} onChange={(event) => updateField("bio", event.target.value)} className="admin-input mt-2" rows={6} />
            </label>
          </div>

          <div className="border-t border-slate-200 pt-5">
            <h2 className="text-lg font-bold">Social profiles</h2>
            <div className="mt-4 grid gap-5 sm:grid-cols-2">
              <label className="admin-label">X / Twitter
                <input type="url" value={form.x_url} onChange={(event) => updateField("x_url", event.target.value)} className="admin-input mt-2" placeholder="https://x.com/..." />
              </label>
              <label className="admin-label">LinkedIn
                <input type="url" value={form.linkedin_url} onChange={(event) => updateField("linkedin_url", event.target.value)} className="admin-input mt-2" placeholder="https://linkedin.com/in/..." />
              </label>
              <label className="admin-label">Instagram
                <input type="url" value={form.instagram_url} onChange={(event) => updateField("instagram_url", event.target.value)} className="admin-input mt-2" placeholder="https://instagram.com/..." />
              </label>
            </div>
          </div>
        </div>

        <aside className="space-y-4 self-start lg:sticky lg:top-6">
          <div className="admin-card p-5 text-center">
            {photoPreview ? (
              <img src={photoPreview} alt="" className="mx-auto h-28 w-28 rounded-full object-cover" />
            ) : (
              <div className="mx-auto grid h-28 w-28 place-items-center rounded-full bg-[#1d282d] font-display text-4xl font-bold text-[#f4ae35]">
                {(form.name || "R").slice(0, 1).toUpperCase()}
              </div>
            )}
            <p className="mt-4 font-bold">{form.name || "Editor name"}</p>
            <p className="mt-1 text-sm text-slate-500">{form.job_title || "Role"}</p>
            {photoPreview && (
              <button type="button" onClick={clearPhoto} className="mt-4 text-xs font-bold text-red-600 hover:text-red-800">
                Remove photo
              </button>
            )}
          </div>
          {error && <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
          <button type="submit" disabled={saveEditor.isPending} className="admin-button-primary w-full">
            {saveEditor.isPending ? "Saving..." : "Save editor"}
          </button>
        </aside>
      </form>
    </div>
  );
}
