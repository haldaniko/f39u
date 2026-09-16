import { useState } from "react";
import { Link } from "react-router-dom";

import newsletterPortrait from "../assets/newsletter-popup-portrait.png";
import arrowRightOutline from "../assets/solar_arrow-right-outline.svg";
import { estimateReadingTime } from "../utils/formatters";

export const fallbackImage = "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1800&q=80";

function Icon({ children, className = "h-4 w-4" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {children}
    </svg>
  );
}

export function SearchIcon({ className }) {
  return (
    <Icon className={className}>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </Icon>
  );
}

export function MailIcon({ className }) {
  return (
    <Icon className={className}>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </Icon>
  );
}

export function MenuIcon({ className }) {
  return (
    <Icon className={className}>
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </Icon>
  );
}

export function MoonIcon({ className }) {
  return (
    <Icon className={className}>
      <path d="M20 14.5A7.5 7.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5Z" />
    </Icon>
  );
}

export function SunIcon({ className }) {
  return (
    <Icon className={className}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="m17.66 17.66 1.41 1.41" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.34 17.66-1.41 1.41" />
      <path d="m19.07 4.93-1.41 1.41" />
    </Icon>
  );
}

function TagIcon() {
  return (
    <Icon className="h-3 w-3">
      <path d="M20 10 14 4H5v9l6 6 9-9Z" />
      <path d="M8 8h.01" />
    </Icon>
  );
}

function ArrowUpIcon() {
  return (
    <Icon className="h-5 w-5">
      <path d="M12 19V5" />
      <path d="m5 12 7-7 7 7" />
    </Icon>
  );
}

function LinkIcon() {
  return (
    <Icon className="h-7 w-7">
      <path d="M10 13a5 5 0 0 0 7.07 0l2.12-2.12a5 5 0 0 0-7.07-7.07L11 4.93" />
      <path d="M14 11a5 5 0 0 0-7.07 0L4.81 13.12a5 5 0 0 0 7.07 7.07L13 19.07" />
    </Icon>
  );
}

export function MetaRow({ article, compact = false }) {
  const category = article?.category?.name || "Art";
  const readTime = estimateReadingTime(article?.rewritten_content || article?.summary || article?.title || "");

  return (
    <div className={`flex items-center gap-4 font-ui text-[10px] font-bold uppercase tracking-[0.08em] ${compact ? "justify-between" : ""}`}>
      <span className="inline-flex items-center gap-1 text-amber-500">
        <TagIcon />
        {category}
      </span>
      <span className="ml-auto text-slate-500 dark:text-slate-400">{readTime}</span>
      {compact && <span className="hidden text-slate-500 dark:text-slate-400 sm:inline">{article?.source_name || "Investor.bg"}</span>}
    </div>
  );
}

export function StoryCard({ article, variant = "default", image = true }) {
  const title = article?.title || "Art Basel brings fun back to the fair with the element of surprise";
  const href = article?.slug ? `/article/${article.slug}` : "/search";
  const source = article?.source_name || "Investor.bg";

  if (variant === "line") {
    return (
      <Link to={href} className="block rounded-lg border-b border-sky-200/70 bg-white px-5 py-4 transition hover:text-accent-700 dark:border-slate-700 dark:bg-[#233133]">
        <h3 className="font-body text-xl font-semibold leading-tight">{title}</h3>
        <div className="mt-4">
          <MetaRow article={article} compact />
        </div>
      </Link>
    );
  }

  return (
    <Link to={href} className="group block overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-1 hover:shadow-xl dark:bg-[#233133] dark:ring-slate-700">
      {image && (
        <div className={variant === "large" ? "h-64 bg-slate-200 dark:bg-slate-300" : "h-44 bg-slate-200 dark:bg-slate-300"}>
          {article?.image_url && (
            <img src={article.image_url} alt={title} className="h-full w-full object-cover transition duration-300 group-hover:scale-105" loading="lazy" />
          )}
        </div>
      )}
      <div className={variant === "large" ? "p-5" : "p-4"}>
        <p className="font-ui text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">{source}</p>
        <h3 className={`${variant === "large" ? "mt-4 text-2xl" : "mt-2 text-xl"} font-body font-semibold leading-tight`}>
          {title}
        </h3>
        {variant === "large" && article?.summary && (
          <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{article.summary}</p>
        )}
        <div className="mt-4">
          <MetaRow article={article} compact={variant !== "large"} />
        </div>
      </div>
    </Link>
  );
}

export function CategoryStrip({ categories = [], title = "Browse by category", nextTitle }) {
  const fallback = ["Culture", "Startups", "Art", "Business", "Feminism"].map((name) => ({
    name,
    slug: name.toLowerCase(),
  }));
  const items = categories.length ? categories.slice(0, 5) : fallback;

  return (
    <section className="category-strip-exact">
      <div className="category-strip-exact__inner">
        <div className="category-strip-exact__heading">
          <h2>{title}</h2>
          <span className="category-strip-exact__dot" aria-hidden="true" />
          <span className="category-strip-exact__line" aria-hidden="true" />
        </div>
        <div className="category-strip-exact__cards">
          {items.map((category) => (
            <Link key={category.slug} to={`/category/${category.slug}`} className="category-strip-exact__card">
              <span className="category-strip-exact__count">20</span>
              <h3>{category.name}</h3>
              <span className="category-strip-exact__arrow" aria-hidden="true">
                <img src={arrowRightOutline} alt="" />
              </span>
            </Link>
          ))}
          <Link to="/search" className="category-strip-exact__see-all">See all</Link>
        </div>
        {nextTitle && (
          <div className="category-strip-exact__next">
            <span className="category-strip-exact__next-line" aria-hidden="true" />
            <span className="category-strip-exact__next-dot" aria-hidden="true" />
            <h2>{nextTitle}</h2>
          </div>
        )}
      </div>
    </section>
  );
}

export function SectionRuleTitle({ title }) {
  return (
    <div className="flex items-center gap-5">
      <h2 className="shrink-0 font-ui text-sm font-bold uppercase tracking-wide">{title}</h2>
      <div className="h-px flex-1 bg-slate-300 dark:bg-slate-600" />
    </div>
  );
}

export function NewsletterBand() {
  return (
    <section className="grid gap-10 py-16 md:grid-cols-[1fr_520px] md:items-center">
      <div>
        <h2 className="max-w-xl font-primary text-3xl font-bold uppercase leading-tight tracking-normal md:text-4xl">
          Stay <span className="text-amber-400">up to date</span> with the world's latest stories.
        </h2>
        <p className="mt-12 font-ui text-sm font-semibold text-slate-500 dark:text-slate-400">
          Copyright 2026 Future Xclusive Local and Foreign Media
        </p>
      </div>
      <div>
        <form className="flex rounded-full bg-slate-100 p-2 shadow-inner ring-1 ring-slate-200 dark:bg-slate-100 dark:ring-white/20">
          <input
            type="email"
            placeholder="Enter your email"
            className="min-w-0 flex-1 bg-transparent px-5 font-ui text-sm text-slate-900 outline-none placeholder:text-slate-400"
          />
          <button type="submit" className="rounded-full bg-amber-400 px-6 py-3 font-ui text-sm font-bold text-slate-950 hover:bg-amber-300">
            Subscribe
          </button>
        </form>
        <p className="mt-6 max-w-md font-ui text-xs leading-5 text-slate-400">
          By subscribing, you agree to receive our weekly newsletter. You can unsubscribe at any time.
        </p>
        <Link to="/contact" className="mt-10 inline-block font-ui text-sm font-semibold text-slate-500 dark:text-slate-300">Contact Us</Link>
      </div>
    </section>
  );
}

export function NewsletterPopup() {
  const [open, setOpen] = useState(true);

  if (!open) return null;

  return (
    <div className="newsletter-popup" role="dialog" aria-modal="true" aria-labelledby="newsletter-popup-title">
      <button
        type="button"
        className="newsletter-popup__close"
        aria-label="Close newsletter popup"
        onClick={() => setOpen(false)}
      >
        ×
      </button>

      <div className="newsletter-popup__inner">
        <div className="newsletter-popup__visual" aria-hidden="true">
          <span className="newsletter-popup__orbit newsletter-popup__orbit--one" />
          <span className="newsletter-popup__orbit newsletter-popup__orbit--two" />
          <span className="newsletter-popup__orbit newsletter-popup__orbit--three" />
          <img className="newsletter-popup__portrait" src={newsletterPortrait} alt="" />
          <span className="newsletter-popup__badge newsletter-popup__badge--digest">
            <span className="newsletter-popup__emoji" aria-hidden="true">🗓️</span>
            Weekly digest
          </span>
          <span className="newsletter-popup__badge newsletter-popup__badge--readers">
            <span className="newsletter-popup__emoji" aria-hidden="true">🌎</span>
            6K+ readers
          </span>
          <span className="newsletter-popup__badge newsletter-popup__badge--rating">
            <span className="newsletter-popup__emoji" aria-hidden="true">⭐</span>
            4.9
          </span>
        </div>

        <div className="newsletter-popup__content">
          <h2 id="newsletter-popup-title">
            Stay <span>up to date</span> with the world's latest stories.
          </h2>
          <p className="newsletter-popup__lead">
            Sign up to our email newsletters to stay on top of news and opinion.
          </p>
          <form className="newsletter-popup__form" onSubmit={(event) => event.preventDefault()}>
            <input type="email" placeholder="Enter your email" aria-label="Email address" />
            <button type="submit">Subscribe</button>
          </form>
          <p className="newsletter-popup__fineprint">
            By subscribing, you agree to receive our weekly newsletter. You can unsubscribe at any time.
          </p>
        </div>
      </div>
    </div>
  );
}

export function SearchControl() {
  return (
    <form className="hidden w-full max-w-[340px] items-center rounded-full border border-[#60666b] bg-transparent p-1 md:flex">
      <input
        aria-label="Search"
        placeholder="Search..."
        className="min-w-0 flex-1 bg-transparent px-4 font-ui text-sm text-white outline-none placeholder:text-slate-300"
      />
      <button type="submit" className="grid h-9 w-9 place-items-center rounded-full border-2 border-amber-400 text-amber-400">
        <SearchIcon className="h-4 w-4" />
      </button>
    </form>
  );
}

export function IconCircle({ children, label }) {
  return (
    <button type="button" aria-label={label} className="grid h-9 w-9 place-items-center rounded-full border border-[#60666b] text-white">
      {children}
    </button>
  );
}

export function BackToTop() {
  return (
    <a href="#top" className="fixed bottom-8 right-8 z-10 hidden h-10 w-10 place-items-center rounded-full border border-sky-200 text-slate-400 dark:border-slate-600 md:grid">
      <ArrowUpIcon />
    </a>
  );
}

export function ShareLinks() {
  return (
    <div>
      <h2 className="font-ui text-xl font-bold uppercase text-slate-600 dark:text-slate-300">Share to</h2>
      <div className="mt-5 flex items-center gap-6 text-slate-500 dark:text-slate-300">
        <span className="font-display text-3xl">@</span>
        <span className="font-display text-3xl">f</span>
        <span className="font-display text-3xl">X</span>
        <span className="font-display text-3xl">wa</span>
        <LinkIcon />
      </div>
    </div>
  );
}
