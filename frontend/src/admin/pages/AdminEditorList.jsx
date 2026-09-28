import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { deleteAdminEditor, fetchAdminEditors } from "../../services/adminService";

export default function AdminEditorList() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const editors = useQuery({
    queryKey: ["admin", "editors", search],
    queryFn: () => fetchAdminEditors({ search: search || undefined }),
  });
  const removeEditor = useMutation({
    mutationFn: deleteAdminEditor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "editors"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "options"] });
    },
  });
  const items = Array.isArray(editors.data) ? editors.data : editors.data?.results || [];

  const handleDelete = (editor) => {
    if (window.confirm(`Delete editor "${editor.name}"? Their author profile will be removed from associated articles.`)) {
      removeEditor.mutate(editor.id);
    }
  };

  return (
    <div className="mx-auto max-w-7xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="admin-kicker">FXLFM team</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight">Editors</h1>
          <p className="mt-2 text-sm text-slate-500">Create editor profiles and update article author information.</p>
        </div>
        <Link to="/admin/editors/new" className="admin-button-primary">Add editor</Link>
      </div>

      <div className="admin-card mt-7 p-4">
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by name, role or location..."
          className="admin-input max-w-xl"
        />
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {items.map((editor) => (
          <article key={editor.id} className="admin-card flex gap-4 p-5">
            {editor.photo_url ? (
              <img src={editor.photo_url} alt="" className="h-16 w-16 shrink-0 rounded-full object-cover" />
            ) : (
              <div className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-[#1d282d] font-display text-xl font-bold text-[#f4ae35]">
                {editor.name.slice(0, 1).toUpperCase()}
              </div>
            )}
            <div className="min-w-0 flex-1">
              <h2 className="truncate text-lg font-bold">{editor.name}</h2>
              <p className="mt-1 truncate text-sm text-slate-500">{editor.job_title || "Editor"}</p>
              {editor.location && <p className="mt-1 text-xs text-slate-400">{editor.location}</p>}
              <div className="mt-4 flex gap-4 text-sm">
                <Link to={`/admin/editors/${editor.id}/edit`} className="admin-link">Edit</Link>
                <button type="button" onClick={() => handleDelete(editor)} disabled={removeEditor.isPending} className="text-red-600 hover:text-red-800 disabled:opacity-50">Delete</button>
              </div>
            </div>
          </article>
        ))}
      </div>

      {editors.isLoading && <p className="py-14 text-center text-sm text-slate-500">Loading editors...</p>}
      {!editors.isLoading && !items.length && <p className="admin-card mt-4 px-5 py-14 text-center text-sm text-slate-500">No editors found.</p>}
    </div>
  );
}
