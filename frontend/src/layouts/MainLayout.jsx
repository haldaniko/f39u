import { Link } from "react-router-dom";

import { IconCircle, MailIcon, MenuIcon, NewsletterPopup, SearchControl, openNewsletterPopup } from "../components/DesignPrimitives";
import DarkModeToggle from "../components/DarkModeToggle";
import Logo from "../components/Logo";

export default function MainLayout({ children }) {
  return (
    <div id="top" className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-[#60666b] bg-[#1d282d]">
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
            <Link to="/search" className="grid h-9 w-9 place-items-center rounded-full border-2 border-[#60666b] text-white md:hidden">
              <span className="text-sm">⌕</span>
            </Link>
            <button type="button" className="ml-4 text-white" aria-label="Open menu">
              <MenuIcon className="h-7 w-7" />
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4">{children}</main>
      <NewsletterPopup />
    </div>
  );
}
