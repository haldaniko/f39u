import { Link, NavLink } from "react-router-dom";

import DarkModeToggle from "../components/DarkModeToggle";
import Logo from "../components/Logo";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/search", label: "Search" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

export default function MainLayout({ children }) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-white/40 dark:border-slate-700/60 glass">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between gap-4">
          <Logo />
          <nav className="hidden md:flex items-center gap-5">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `font-ui text-sm tracking-wide ${isActive ? "text-accent-700 dark:text-accent-500" : "text-slate-700 dark:text-slate-300"}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <DarkModeToggle />
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
      <footer className="border-t border-slate-200 dark:border-slate-800 mt-12">
        <div className="mx-auto max-w-7xl px-4 py-8 text-sm text-slate-600 dark:text-slate-300">
          <p className="font-ui">Facts 39 Unlimited • Independent global news desk.</p>
          <p className="mt-1">© {new Date().getFullYear()} Facts 39 Unlimited</p>
          <Link to="/about" className="text-brand-700 dark:text-brand-300">Learn more</Link>
        </div>
      </footer>
    </div>
  );
}
