import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { IconCircle, MailIcon, MenuIcon, NewsletterPopup, SearchControl, SearchIcon, openNewsletterPopup } from "../components/DesignPrimitives";
import DarkModeToggle from "../components/DarkModeToggle";
import Logo from "../components/Logo";
import { useCategories } from "../hooks/useNewsQuery";

function CloseIcon({ className = "h-5 w-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <path d="M6 6l12 12" />
      <path d="M18 6L6 18" />
    </svg>
  );
}

export default function MainLayout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const categoriesQuery = useCategories();
  const categories = Array.isArray(categoriesQuery.data)
    ? categoriesQuery.data
    : categoriesQuery.data?.results || [];
  const location = useLocation();

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname, location.search]);

  useEffect(() => {
    if (!menuOpen) return undefined;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    const handlePointerDown = (event) => {
      if (!event.target.closest(".site-header")) setMenuOpen(false);
    };

    window.addEventListener("keydown", handleKeyDown);
    document.addEventListener("pointerdown", handlePointerDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("pointerdown", handlePointerDown);
    };
  }, [menuOpen]);

  return (
    <div id="top" className="min-h-screen">
      <header className="site-header sticky top-0 z-20 border-b border-[#60666b] bg-[#1d282d]">
        <div className="mx-auto grid max-w-7xl grid-cols-[1fr_auto_1fr] items-center gap-4 px-4 py-5">
          <Logo />
          <div className="flex items-center justify-center gap-3">
            <SearchControl />
            <DarkModeToggle />
            <IconCircle label="Open newsletter popup" onClick={openNewsletterPopup}>
              <MailIcon className="h-4 w-4" />
            </IconCircle>
          </div>
          <div className="flex items-center justify-end gap-2">
            <Link to="/search" aria-label="Search" className="grid h-9 w-9 place-items-center rounded-full border-2 border-[#60666b] text-white transition hover:bg-[#60666b] focus-visible:bg-[#60666b] focus-visible:outline-none md:hidden">
              <SearchIcon className="h-4 w-4" />
            </Link>
            <button
              type="button"
              className="ml-4 grid h-9 w-9 place-items-center rounded-full text-white transition hover:bg-[#60666b] focus-visible:bg-[#60666b] focus-visible:outline-none"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen}
              aria-controls="site-navigation-menu"
              onClick={() => setMenuOpen((isOpen) => !isOpen)}
            >
              {menuOpen ? <CloseIcon className="h-6 w-6" /> : <MenuIcon className="h-7 w-7" />}
            </button>
          </div>
        </div>
        {menuOpen && (
          <div id="site-navigation-menu" className="site-menu">
            <div className="site-menu__panel">
              <nav className="site-menu__nav" aria-label="Menu categories">
                {categories.map((category) => (
                  <Link key={category.slug} to={`/category/${category.slug}`} onClick={() => setMenuOpen(false)}>
                    {category.name}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        )}
      </header>
      <main className="mx-auto max-w-7xl px-4">{children}</main>
      <NewsletterPopup />
    </div>
  );
}
