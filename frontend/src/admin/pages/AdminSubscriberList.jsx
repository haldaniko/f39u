import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  deleteAdminSubscriber,
  fetchAdminSubscribers,
  updateAdminSubscriber,
} from "../../services/adminService";

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export default function AdminSubscriberList() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({ search: "", source: "", is_active: "", page: 1 });
  const subscribers = useQuery({
    queryKey: ["admin", "subscribers", filters],
    queryFn: () => fetchAdminSubscribers({
      ...filters,
      search: filters.search || undefined,
      source: filters.source || undefined,
      is_active: filters.is_active || undefined,
    }),
  });
  const updateSubscriber = useMutation({
    mutationFn: ({ id, isActive }) => updateAdminSubscriber(id, { is_active: isActive }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "subscribers"] }),
  });
  const removeSubscriber = useMutation({
    mutationFn: deleteAdminSubscriber,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "subscribers"] }),
  });

  const items = subscribers.data?.results || [];
  const patchFilters = (next) => setFilters((current) => ({ ...current, ...next, page: 1 }));

  const handleDelete = (subscriber) => {
    if (window.confirm(`Delete subscriber "${subscriber.email}"?`)) {
      removeSubscriber.mutate(subscriber.id);
    }
  };

  return (
    <div className="mx-auto max-w-7xl">
      <div>
        <p className="admin-kicker">Newsletter audience</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Subscribers</h1>
        <p className="mt-2 text-sm text-slate-500">View and manage email addresses collected through the website.</p>
      </div>

      <div className="admin-card mt-7 grid gap-3 p-4 md:grid-cols-[minmax(260px,1fr)_180px_180px]">
        <input
          type="search"
          value={filters.search}
          onChange={(event) => patchFilters({ search: event.target.value })}
          placeholder="Search by email..."
          className="admin-input"
        />
        <select value={filters.source} onChange={(event) => patchFilters({ source: event.target.value })} className="admin-input">
          <option value="">All sources</option>
          <option value="footer">Footer</option>
          <option value="popup">Popup</option>
        </select>
        <select value={filters.is_active} onChange={(event) => patchFilters({ is_active: event.target.value })} className="admin-input">
          <option value="">All statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div className="admin-card mt-4 overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-5 py-3">Email</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Subscribed</th>
              <th className="px-5 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((subscriber) => (
              <tr key={subscriber.id} className="hover:bg-slate-50">
                <td className="px-5 py-4 font-bold text-slate-800">{subscriber.email}</td>
                <td className="px-4 py-4 text-slate-600">{subscriber.source_label}</td>
                <td className="px-4 py-4">
                  <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${subscriber.is_active ? "bg-emerald-100 text-emerald-800" : "bg-slate-200 text-slate-600"}`}>
                    {subscriber.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="px-4 py-4 text-xs text-slate-500">{dateFormatter.format(new Date(subscriber.subscribed_at))}</td>
                <td className="whitespace-nowrap px-5 py-4 text-right">
                  <button
                    type="button"
                    onClick={() => updateSubscriber.mutate({ id: subscriber.id, isActive: !subscriber.is_active })}
                    disabled={updateSubscriber.isPending}
                    className="admin-link mr-4 disabled:opacity-50"
                  >
                    {subscriber.is_active ? "Deactivate" : "Activate"}
                  </button>
                  <button type="button" onClick={() => handleDelete(subscriber)} disabled={removeSubscriber.isPending} className="text-red-600 hover:text-red-800 disabled:opacity-50">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {subscribers.isLoading && <p className="px-5 py-12 text-center text-sm text-slate-500">Loading subscribers...</p>}
        {!subscribers.isLoading && !items.length && <p className="px-5 py-12 text-center text-sm text-slate-500">No subscribers match these filters.</p>}
      </div>

      <div className="mt-4 flex items-center justify-between text-sm">
        <span className="text-slate-500">Subscribers: {subscribers.data?.count ?? 0}</span>
        <div className="flex items-center gap-2">
          <button disabled={!subscribers.data?.previous} onClick={() => setFilters((current) => ({ ...current, page: current.page - 1 }))} className="rounded-lg border border-slate-300 px-3 py-2 disabled:opacity-40">Previous</button>
          <span className="px-2 py-2">Page {filters.page}</span>
          <button disabled={!subscribers.data?.next} onClick={() => setFilters((current) => ({ ...current, page: current.page + 1 }))} className="rounded-lg border border-slate-300 px-3 py-2 disabled:opacity-40">Next</button>
        </div>
      </div>
    </div>
  );
}
