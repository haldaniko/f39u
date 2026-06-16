import { NavLink, Outlet } from "react-router-dom";

import { useAdminAuth } from "./AuthContext";

const navigation = [
  { to: "/admin", label: "Overview", end: true },
  { to: "/admin/articles", label: "Articles" },
  { to: "/admin/articles/new", label: "New article" },
];

export default function AdminLayout() {
  const { user, logout } = useAdminAuth();
  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username;

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950 font-ui dark:bg-slate-950 dark:text-slate-100">
      <div className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
        <aside className="bg-slate-950 text-white px-5 py-6 lg:fixed lg:inset-y-0 lg:w-[250px]">
          <a href="/" className="block">
            <span className="text-xs uppercase tracking-[0.28em] text-teal-300">FXLFM</span>
            <span className="block mt-1 text-xl font-semibold">Newsroom</span>
          </a>
          <nav className="mt-8 grid grid-cols-3 gap-2 lg:grid-cols-1">
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `rounded-xl px-3 py-2.5 text-sm transition ${
                    isActive ? "bg-teal-500 text-slate-950" : "text-slate-300 hover:bg-white/10 hover:text-white"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-8 border-t border-white/10 pt-5 lg:absolute lg:bottom-6 lg:left-5 lg:right-5">
            <p className="truncate text-sm font-medium">{displayName}</p>
            <p className="truncate text-xs text-slate-400">{user?.email || "Administrator"}</p>
            <div className="mt-3 flex gap-3 text-xs">
              <a href="/" className="text-teal-300 hover:text-teal-200">Open site</a>
              <button type="button" onClick={logout} className="text-slate-400 hover:text-white">Sign out</button>
            </div>
          </div>
        </aside>
        <main className="min-w-0 px-4 py-6 sm:px-7 lg:col-start-2 lg:px-10 lg:py-9">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
