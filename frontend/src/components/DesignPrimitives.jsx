import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import newsletterPortrait from "../assets/newsletter-popup-portrait.png";
import arrowRightOutline from "../assets/solar_arrow-right-outline.svg";
import pinIcon from "../assets/vector.svg";
import facebookIcon from "../assets/article-share/facebook.svg";
import linkIcon from "../assets/article-share/link.svg";
import threadsIcon from "../assets/article-share/threads.svg";
import whatsappIcon from "../assets/article-share/whatsapp.svg";
import xIcon from "../assets/article-share/x.svg";
import { estimateReadingTime } from "../utils/formatters";

const newsletterPopupSessionKey = "fxlfm-newsletter-popup-shown";
const newsletterPopupOpenEvent = "fxlfm:open-newsletter-popup";

export function openNewsletterPopup() {
  window.dispatchEvent(new Event(newsletterPopupOpenEvent));
}

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

function ArrowUpIcon() {
  return (
    <Icon className="h-5 w-5">
      <path d="M12 19V5" />
      <path d="m5 12 7-7 7 7" />
    </Icon>
  );
}

export function MetaRow({ article, compact = false }) {
  const category = article?.category?.name || "News";
  const readTime = estimateReadingTime(article?.rewritten_content || article?.summary || article?.title || "");

  return (
    <div className={`flex items-center gap-4 font-ui text-[10px] font-bold uppercase tracking-[0.08em] ${compact ? "justify-between" : ""}`}>
      <span className="inline-flex items-center gap-1 text-amber-500">
        <img src={pinIcon} alt="" className="h-3 w-3" aria-hidden="true" />
        {category}
      </span>
      <span className="ml-auto text-slate-500 dark:text-slate-400">{readTime}</span>
      {compact && <span className="hidden text-slate-500 dark:text-slate-400 sm:inline">{article?.source_name || "FXLFM"}</span>}
    </div>
  );
}

export function StoryCard({ article, variant = "default", image = true, className = "", imageClassName = "", contentClassName = "" }) {
  const contentRef = useRef(null);
  const sourceRef = useRef(null);
  const titleRef = useRef(null);
  const textRef = useRef(null);
  const metaRef = useRef(null);
  const [textBoxStyle, setTextBoxStyle] = useState(null);

  const title = article?.title || "";
  const storyText = article?.rewritten_content || article?.summary || "";
  const href = article?.slug ? `/article/${article.slug}` : "/search";
  const source = article?.source_name || "FXLFM";
  const isLarge = variant === "large";
  const isPopular = variant === "popular";
  const isPopularCompact = variant === "popularCompact";
  const isRelated = variant === "related";
  const isGridCard = Boolean(className);
  const showImage = image && !isPopularCompact;
  const defaultImageClassName = isLarge ? "h-64" : isPopular ? "h-24" : "h-44";
  const shouldClampText = isLarge || isPopular || isPopularCompact;
  const textMarginClassName = isLarge ? "mt-4" : isPopular ? "mt-2" : "mt-3";

  useLayoutEffect(() => {
    if (!shouldClampText || !isGridCard) {
      setTextBoxStyle(null);
      return undefined;
    }

    const elements = [contentRef.current, sourceRef.current, titleRef.current, textRef.current, metaRef.current].filter(Boolean);
    if (elements.length < 5) return undefined;

    const readPixels = (value) => {
      const parsed = parseFloat(value);
      return Number.isFinite(parsed) ? parsed : 0;
    };

    const updateLineClamp = () => {
      const content = contentRef.current;
      const source = sourceRef.current;
      const titleElement = titleRef.current;
      const text = textRef.current;
      const meta = metaRef.current;

      if (!content || !source || !titleElement || !text || !meta) return;

      const titleStyles = window.getComputedStyle(titleElement);
      const textStyles = window.getComputedStyle(text);
      const lineHeight = readPixels(textStyles.lineHeight) || (isLarge ? 24 : 20);
      const metaStyles = window.getComputedStyle(meta);
      const safeGap = isLarge ? 24 : 28;
      const availableHeight =
        content.clientHeight -
        source.offsetHeight -
        readPixels(titleStyles.marginTop) -
        titleElement.offsetHeight -
        readPixels(textStyles.marginTop) -
        meta.offsetHeight -
        readPixels(metaStyles.paddingTop) -
        safeGap;
      const nextLineClamp = Math.max(1, Math.floor(availableHeight / lineHeight));
      const nextStyle = {
        display: "-webkit-box",
        WebkitBoxOrient: "vertical",
        WebkitLineClamp: nextLineClamp,
        height: `${nextLineClamp * lineHeight}px`,
        maxHeight: `${nextLineClamp * lineHeight}px`,
      };

      setTextBoxStyle((current) => {
        if (
          current?.WebkitLineClamp === nextStyle.WebkitLineClamp &&
          current?.maxHeight === nextStyle.maxHeight
        ) {
          return current;
        }
        return nextStyle;
      });
    };

    updateLineClamp();

    const resizeObserver = new ResizeObserver(updateLineClamp);
    elements.forEach((element) => resizeObserver.observe(element));
    window.addEventListener("resize", updateLineClamp);
    document.fonts?.ready?.then(updateLineClamp);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener("resize", updateLineClamp);
    };
  }, [isGridCard, isLarge, shouldClampText, storyText, title]);

  if (!article) return null;

  if (variant === "line") {
    return (
      <Link to={href} className={`block rounded-lg border-b border-sky-200/70 bg-white px-5 py-4 transition hover:text-accent-700 dark:border-slate-700 dark:bg-[#233133] ${className}`}>
        <h3 className="font-body text-xl font-semibold leading-tight">{title}</h3>
        <div className="mt-4">
          <MetaRow article={article} compact />
        </div>
      </Link>
    );
  }

  return (
    <Link to={href} className={`group min-w-0 ${isGridCard || isRelated ? "flex h-full flex-col" : "block"} overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-1 hover:shadow-xl dark:bg-[#233133] dark:ring-slate-700 ${className}`}>
      {showImage && (
        <div className={`${imageClassName || defaultImageClassName} shrink-0 bg-slate-200 dark:bg-slate-300`}>
          {article?.image_url && (
            <img src={article.image_url} alt={title} className="h-full w-full object-cover transition duration-300 group-hover:scale-105" loading="lazy" />
          )}
        </div>
      )}
      <div ref={contentRef} className={`${contentClassName || (isLarge ? "p-5" : isPopular || isPopularCompact ? "p-3" : "p-4")} ${isGridCard || isRelated ? "flex min-h-0 flex-1 flex-col" : ""}`}>
        <p ref={sourceRef} className="shrink-0 font-ui text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">{source}</p>
        <h3 ref={titleRef} className={`${isLarge ? "mt-4 text-2xl" : isPopular || isPopularCompact ? "mt-2 text-base" : "mt-2 text-xl"} shrink-0 font-body font-semibold leading-tight`}>
          {title}
        </h3>
        {isLarge && (
          <p ref={textRef} className={`${textMarginClassName} shrink-0 overflow-hidden text-sm leading-6 text-slate-600 dark:text-slate-300`} style={textBoxStyle || undefined}>{storyText}</p>
        )}
        {(isPopular || isPopularCompact) && (
          <p ref={textRef} className={`${textMarginClassName} shrink-0 overflow-hidden text-xs leading-5 text-slate-600 dark:text-slate-300`} style={textBoxStyle || undefined}>{storyText}</p>
        )}
        {isRelated && storyText && (
          <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{storyText}</p>
        )}
        <div ref={metaRef} className={isGridCard || isRelated ? "mt-auto shrink-0 pt-5" : "mt-4"}>
          <MetaRow article={article} compact={!isLarge} />
        </div>
      </div>
    </Link>
  );
}

export function CategoryStrip({ categories = [], title = "Browse by category", nextTitle }) {
  const items = categories.slice(0, 5);
  const extraItems = categories.slice(5);
  const [expanded, setExpanded] = useState(false);

  if (!items.length) return null;

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
          {extraItems.length > 0 && (
            <button
              type="button"
              className="category-strip-exact__see-all"
              aria-expanded={expanded}
              onClick={() => setExpanded((value) => !value)}
            >
              {expanded ? "Hide" : "See all"}
            </button>
          )}
        </div>
        {extraItems.length > 0 && (
          <div className={`category-strip-exact__extra ${expanded ? "category-strip-exact__extra--open" : ""}`}>
            <div className="category-strip-exact__extra-grid">
              {extraItems.map((category) => (
                <Link key={category.slug} to={`/category/${category.slug}`} className="category-strip-exact__card">
                  <span className="category-strip-exact__count">20</span>
                  <h3>{category.name}</h3>
                  <span className="category-strip-exact__arrow" aria-hidden="true">
                    <img src={arrowRightOutline} alt="" />
                  </span>
                </Link>
              ))}
            </div>
          </div>
        )}
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
  const [open, setOpen] = useState(() => {
    if (typeof window === "undefined") return false;
    return sessionStorage.getItem(newsletterPopupSessionKey) !== "true";
  });

  useEffect(() => {
    if (open) {
      sessionStorage.setItem(newsletterPopupSessionKey, "true");
    }
  }, [open]);

  useEffect(() => {
    const handleOpen = () => setOpen(true);

    window.addEventListener(newsletterPopupOpenEvent, handleOpen);
    return () => window.removeEventListener(newsletterPopupOpenEvent, handleOpen);
  }, []);

  if (!open) return null;

  return (
    <div className="newsletter-popup" role="dialog" aria-modal="true" aria-labelledby="newsletter-popup-title">
      <button
        type="button"
        className="newsletter-popup__close"
        aria-label="Close newsletter popup"
        onClick={() => setOpen(false)}
      >
        <svg className="newsletter-popup__close-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>

      <div className="newsletter-popup__inner">
        <div className="newsletter-popup__visual" aria-hidden="true">
          <span className="newsletter-popup__orbit newsletter-popup__orbit--one" />
          <span className="newsletter-popup__orbit newsletter-popup__orbit--two" />
          <span className="newsletter-popup__orbit newsletter-popup__orbit--three" />
          <img className="newsletter-popup__portrait" src={newsletterPortrait} alt="" />
          <span className="newsletter-popup__badge newsletter-popup__badge--digest">
            <img className="newsletter-popup__emoji" src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f5d3.svg" alt="" aria-hidden="true" />
            Weekly digest
          </span>
          <span className="newsletter-popup__badge newsletter-popup__badge--readers">
            <img className="newsletter-popup__emoji" src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f30e.svg" alt="" aria-hidden="true" />
            6K+ readers
          </span>
          <span className="newsletter-popup__badge newsletter-popup__badge--rating">
            <img className="newsletter-popup__emoji" src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/2b50.svg" alt="" aria-hidden="true" />
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
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmedQuery = query.trim();

    if (trimmedQuery) {
      navigate(`/search?q=${encodeURIComponent(trimmedQuery)}`);
    } else {
      navigate("/search");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative hidden h-9 w-[300px] items-center rounded-full border border-[#60666b] bg-transparent md:flex lg:w-[340px]">
      <input
        aria-label="Search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search..."
        className="min-w-0 flex-1 bg-transparent py-0 pl-4 pr-12 font-ui text-sm text-white outline-none placeholder:text-slate-300"
      />
      <button type="submit" className="absolute -right-1 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full border-2 border-amber-400 bg-[#1d282d] text-amber-400 transition hover:bg-amber-400 hover:text-[#1d282d] focus-visible:bg-amber-400 focus-visible:text-[#1d282d] focus-visible:outline-none">
        <SearchIcon className="h-4 w-4" />
      </button>
    </form>
  );
}

export function IconCircle({ children, label, onClick }) {
  return (
    <button type="button" aria-label={label} onClick={onClick} className="grid h-9 w-9 place-items-center rounded-full border-2 border-[#60666b] text-white transition hover:bg-[#60666b] focus-visible:bg-[#60666b] focus-visible:outline-none">
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
  const links = [
    { label: "Share on Threads", icon: threadsIcon },
    { label: "Share on Facebook", icon: facebookIcon },
    { label: "Share on X", icon: xIcon },
    { label: "Share on WhatsApp", icon: whatsappIcon },
    { label: "Copy article link", icon: linkIcon },
  ];

  return (
    <div>
      <h2 className="font-ui text-xl font-bold uppercase text-slate-600 dark:text-slate-300">Share to</h2>
      <div className="mt-5 flex items-center gap-5">
        {links.map((item) => (
          <button
            key={item.label}
            type="button"
            aria-label={item.label}
            className="grid h-10 w-10 place-items-center rounded-full transition hover:bg-slate-200 focus-visible:bg-slate-200 focus-visible:outline-none dark:hover:bg-slate-700 dark:focus-visible:bg-slate-700"
          >
            <img src={item.icon} alt="" aria-hidden="true" className="max-h-8 max-w-8" />
          </button>
        ))}
      </div>
    </div>
  );
}
