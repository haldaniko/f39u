import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import {
  BackToTop,
  CategoryStrip,
  NewsletterBand,
  StoryCard,
  fallbackImage,
} from "../components/DesignPrimitives";
import PageSkeleton from "../components/PageSkeleton";
import Seo from "../components/Seo";
import { useAuthor, useCategories, useInfiniteNews, useTrending } from "../hooks/useNewsQuery";
import { estimateReadingTime } from "../utils/formatters";

const fallbackHero = {
  title: "Art Basel brings fun back to the fair with the element of surprise",
  summary: "In a surprising turn of events, a rare species of butterfly, previously thought to be extinct, has been spotted in the lush forests of Evergreen Valley.",
  slug: "search",
  source_name: "Investor.bg",
  image_url: fallbackImage,
  category: { name: "Art", slug: "art" },
};

const fallbackCard = {
  ...fallbackHero,
  image_url: null,
};

const staticHeroImage = "https://images.unsplash.com/photo-1557683316-973673baf926?auto=format&fit=crop&w=2400&q=80";

function pickStories(articles, trending) {
  const pool = [...articles, ...trending].filter(Boolean);
  return Array.from({ length: 14 }, (_, index) => pool[index % Math.max(pool.length, 1)] || fallbackCard);
}

export default function HomePage() {
  const newsQuery = useInfiniteNews();
  const trendingQuery = useTrending();
  const categoriesQuery = useCategories();
  const authorQuery = useAuthor("maria-nicholson");

  const articles = newsQuery.data?.pages.flatMap((page) => page.results || []) || [];
  const trending = Array.isArray(trendingQuery.data)
    ? trendingQuery.data
    : trendingQuery.data?.results || [];
  const categories = Array.isArray(categoriesQuery.data)
    ? categoriesQuery.data
    : categoriesQuery.data?.results || [];
  const hero = articles[0] || fallbackHero;
  const heroHref = articles[0] ? `/article/${hero.slug}` : "/search";
  const heroReadTime = estimateReadingTime(hero.rewritten_content || hero.summary || hero.title);
  const stories = pickStories(articles.slice(1), trending);
  const editor = authorQuery.data && typeof authorQuery.data === "object" ? authorQuery.data : null;

  const seo = (
    <Seo
      title="Latest Global News & Breaking Stories | FXLFM"
      description="Read the latest global news, breaking stories and clear reporting across business, technology, politics, science and culture at FXLFM."
      path="/"
      image={staticHeroImage}
    />
  );

  if (newsQuery.isLoading) {
    return <>{seo}<PageSkeleton /></>;
  }

  return (
    <>
      {seo}
      <div className="space-y-16 pb-4 pt-0">
        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          className="home-hero relative left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] w-screen overflow-hidden bg-[#172322] text-white"
        >
          <img
            src={staticHeroImage}
            alt=""
            className="absolute inset-0 h-full w-full scale-110 object-cover opacity-70 blur-[1px] saturate-125"
            aria-hidden="true"
          />
          <div className="home-hero-motion absolute inset-0" aria-hidden="true" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#172322]/88 via-[#31523b]/28 to-[#b7e6b2]/18" aria-hidden="true" />
          <div className="relative mx-auto grid min-h-[590px] max-w-7xl items-center gap-10 px-4 py-20 md:grid-cols-[1fr_420px]">
            <div className="max-w-2xl">
              <h1 className="font-display text-5xl font-bold uppercase leading-[0.94] tracking-normal sm:text-6xl lg:text-7xl">
                Independent Newsroom Platform
              </h1>
              <div className="mt-7 h-1 w-16 bg-accent-500" />
              <p className="mt-5 font-ui text-sm font-bold uppercase tracking-[0.18em] text-white/90">
                100+ news articles in real time
              </p>
            </div>

            <Link
              to={heroHref}
              className="group overflow-hidden rounded-lg bg-white text-slate-950 shadow-2xl ring-1 ring-black/5 transition duration-200 hover:-translate-y-1 dark:bg-[#233133] dark:text-white"
            >
              <div className="h-56 bg-slate-200 dark:bg-slate-300">
                <img
                  src={hero.image_url || fallbackImage}
                  alt={hero.title}
                  className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                />
              </div>
              <div className="p-5">
                <p className="font-ui text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">
                  {hero.source_name || "Investor.bg"}
                </p>
                <h2 className="mt-3 font-body text-2xl font-semibold leading-tight">{hero.title}</h2>
                <div className="mt-5 flex items-center justify-between gap-3 font-ui text-[10px] font-bold uppercase tracking-[0.08em]">
                  <span className="rounded-sm bg-red-500 px-2 py-1 text-white">Breaking News</span>
                  <span className="text-slate-500 dark:text-slate-400">{heroReadTime}</span>
                </div>
              </div>
            </Link>
          </div>
        </motion.section>

        <CategoryStrip categories={categories} nextTitle="Popular now" />

        <section>
          <div className="grid gap-6 lg:grid-cols-[1.35fr_0.9fr_0.9fr] lg:grid-rows-[210px_250px_190px_230px_210px]">
            <StoryCard article={stories[0]} variant="large" className="lg:col-start-1 lg:row-span-2 lg:row-start-1" />
            <StoryCard article={stories[7]} variant="popularCompact" className="lg:col-start-1 lg:row-start-3" />
            <StoryCard article={stories[8]} variant="popular" className="lg:col-start-1 lg:row-span-2 lg:row-start-4" />

            <StoryCard article={stories[1]} variant="popularCompact" className="lg:col-start-2 lg:row-start-1" />
            <StoryCard article={stories[2]} variant="popular" className="lg:col-start-2 lg:row-span-2 lg:row-start-2" />
            <StoryCard article={stories[3]} variant="popularCompact" className="lg:col-start-2 lg:row-start-4" />
            <StoryCard article={stories[4]} variant="popularCompact" className="lg:col-start-2 lg:row-start-5" />

            <div className="grid h-full place-items-center rounded-md bg-[#282524] text-sm font-semibold uppercase text-white dark:bg-white dark:text-slate-900 lg:col-start-3 lg:row-span-2 lg:row-start-1">Advert</div>
            <StoryCard article={stories[5]} variant="popularCompact" className="lg:col-start-3 lg:row-start-3" />
            <StoryCard article={stories[6]} variant="popularCompact" className="lg:col-start-3 lg:row-start-4" />
            <StoryCard article={stories[9]} variant="popularCompact" className="lg:col-start-3 lg:row-start-5" />
          </div>
        </section>

        {editor && (
          <section className="mx-auto max-w-lg text-center">
            <h2 className="font-ui text-sm font-bold uppercase tracking-wide">Meet the editor(s)</h2>
            <div className="mt-8 grid items-center gap-4 sm:grid-cols-[150px_1fr] sm:text-left">
              <img src={editor.photo_url} alt={editor.name} className="mx-auto h-32 w-32 rounded-full object-cover" />
              <div>
                <span className="rounded-full bg-amber-400 px-3 py-1 font-ui text-xs font-bold text-slate-950">1-st editor</span>
                <p className="mt-5 font-display text-xl font-bold">{editor.name}</p>
                <p className="font-ui text-xs text-slate-500 dark:text-slate-400">{editor.job_title}</p>
              </div>
              <p className="rounded-md bg-white p-4 text-left text-xs leading-5 text-slate-600 shadow-sm dark:bg-[#233133] dark:text-slate-300 sm:col-start-2">
                {editor.bio}
              </p>
            </div>
          </section>
        )}

        <section>
          <h2 className="text-center font-ui text-sm font-bold uppercase tracking-wide">Latest feed</h2>
          <div className="mt-8 grid gap-8 lg:grid-cols-3">
            <div className="space-y-4">
              <StoryCard article={stories[7]} />
              <StoryCard article={stories[8]} variant="line" />
              <StoryCard article={stories[9]} variant="line" />
              <StoryCard article={stories[10]} variant="line" />
            </div>
            <div className="space-y-4">
              <StoryCard article={stories[11]} />
              <StoryCard article={stories[12]} variant="line" />
              <StoryCard article={stories[13]} variant="line" />
              <StoryCard article={stories[2]} variant="line" />
            </div>
            <div className="space-y-4">
              <StoryCard article={stories[3]} variant="line" />
              <StoryCard article={stories[4]} variant="line" />
              <StoryCard article={stories[5]} variant="line" />
              <StoryCard article={stories[6]} />
            </div>
          </div>
          {newsQuery.hasNextPage && (
            <div className="mt-8 text-center">
              <button type="button" onClick={() => newsQuery.fetchNextPage()} className="font-ui text-sm font-bold text-slate-400">
                Load More ◢
              </button>
            </div>
          )}
        </section>

        <NewsletterBand />
      </div>
      <BackToTop />
    </>
  );
}
