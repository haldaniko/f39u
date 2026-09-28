import { NavLink, Outlet } from "react-router-dom";

import { useAdminAuth } from "./AuthContext";

const navigation = [
  { to: "/admin", label: "Overview", end: true },
  { to: "/admin/articles", label: "Articles" },
  { to: "/admin/articles/new", label: "New article" },
  { to: "/admin/editors", label: "Editors" },
  { to: "/admin/subscribers", label: "Subscribers" },
];

export default function AdminLayout() {
  const { user, logout } = useAdminAuth();
  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username;

  return (
    <div className="admin-shell min-h-screen text-slate-950">
      <div className="min-h-screen lg:grid lg:grid-cols-[260px_1fr]">
        <aside className="admin-sidebar px-5 py-6 text-white lg:fixed lg:inset-y-0 lg:w-[260px]">
          <a href="/" className="block border-b border-white/15 pb-6">
            <span className="font-display text-2xl font-bold uppercase leading-none">FXLFM</span>
            <span className="mt-2 block font-ui text-[10px] font-bold uppercase tracking-[0.2em] text-[#f4ae35]">Editorial desk</span>
          </a>
          <nav className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-1">
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) => `admin-nav-link ${isActive ? "admin-nav-link--active" : ""}`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-8 border-t border-white/15 pt-5 lg:absolute lg:bottom-6 lg:left-5 lg:right-5">
            <p className="truncate font-ui text-sm font-bold">{displayName}</p>
            <p className="mt-1 truncate font-ui text-xs text-slate-400">{user?.email || "Administrator"}</p>
            <div className="mt-4 flex gap-4 font-ui text-xs">
              <a href="/" className="text-[#f4ae35] hover:text-[#ffd27e]">Open website</a>
              <button type="button" onClick={logout} className="text-slate-400 hover:text-white">Sign out</button>
            </div>
          </div>
        </aside>
        <main className="admin-main min-w-0 px-4 py-7 sm:px-7 lg:col-start-2 lg:px-10 lg:py-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
