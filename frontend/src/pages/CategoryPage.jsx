import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";

import {
  BackToTop,
  CategoryStrip,
  NewsletterBand,
  StoryCard,
} from "../components/DesignPrimitives";
import PageSkeleton from "../components/PageSkeleton";
import Seo, { withBrand } from "../components/Seo";
import { useCategories, useInfiniteNews } from "../hooks/useNewsQuery";
import { estimateReadingTime } from "../utils/formatters";

function fillStories(items) {
  if (!items.length) return [];
  return Array.from({ length: 12 }, (_, index) => items[index % items.length]);
}

export default function CategoryPage() {
  const { slug } = useParams();
  const newsQuery = useInfiniteNews();
  const categoriesQuery = useCategories();
  const all = newsQuery.data?.pages.flatMap((page) => page.results || []) || [];
  const categories = Array.isArray(categoriesQuery.data)
    ? categoriesQuery.data
    : categoriesQuery.data?.results || [];
  const category = categories.find((item) => item.slug === slug);
  const categoryName = category?.name || slug.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
  const description = category?.description || `Latest ${categoryName} news, stories and developments curated by FXLFM.`;

  const filtered = useMemo(
    () => all.filter((article) => article.category?.slug === slug || article.category?.name?.toLowerCase() === slug),
    [all, slug]
  );
  const stories = fillStories(filtered);
  const hero = stories[0];

  if (newsQuery.isLoading || categoriesQuery.isLoading) {
    return (
      <>
        <Seo title={withBrand(`${categoryName} News`)} description={description} path={`/category/${slug}`} />
        <PageSkeleton />
      </>
    );
  }

  return (
    <>
      <Seo title={withBrand(`${categoryName} News`)} description={description} path={`/category/${slug}`} />
      <section className="space-y-16 pb-4 pt-10">
        <nav className="font-ui text-sm font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          <Link to="/">Home</Link>
          <span className="mx-2">/</span>
          <span className="text-slate-950 dark:text-white">{categoryName}</span>
        </nav>

        {hero ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <Link to={`/article/${hero.slug}`} className="block overflow-hidden rounded-lg bg-slate-200 dark:bg-slate-300">
              {hero.image_url && (
                <img
                  src={hero.image_url}
                  alt={hero.title}
                  className="h-[420px] w-full object-cover"
                />
              )}
            </Link>
            <Link to={`/article/${hero.slug}`} className="rounded-lg bg-white p-8 shadow-sm ring-1 ring-slate-100 dark:bg-[#233133] dark:ring-slate-700">
              <div className="flex justify-between font-ui text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                <span>{hero.source_name || "FXLFM"}</span>
                <span>{estimateReadingTime(hero.rewritten_content || hero.summary || hero.title)}</span>
              </div>
              <h1 className="mt-8 font-body text-5xl font-bold leading-tight">{hero.title}</h1>
              <p className="mt-8 line-clamp-6 font-ui text-2xl leading-9 text-slate-500 dark:text-slate-300">
                {hero.summary || description}
              </p>
            </Link>
          </div>
        ) : (
          <p className="rounded-lg bg-white p-6 text-sm text-slate-500 shadow-sm ring-1 ring-slate-200 dark:bg-[#233133] dark:ring-slate-700">
            No published articles in this category yet.
          </p>
        )}

        {stories.length > 1 && (
          <div className="grid gap-6 lg:grid-cols-[1fr_1fr_0.9fr] lg:grid-rows-[220px_220px_200px_200px_240px]">
            <StoryCard article={stories[1]} variant="popular" imageClassName="h-44" contentClassName="p-4" className="lg:col-start-1 lg:row-span-2 lg:row-start-1" />
            <StoryCard article={stories[2]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-1 lg:row-start-3" />
            <StoryCard article={stories[3]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-1 lg:row-start-4" />
            <StoryCard article={stories[4]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-1 lg:row-start-5" />

            <StoryCard article={stories[5]} variant="popular" imageClassName="h-44" contentClassName="p-4" className="lg:col-start-2 lg:row-span-2 lg:row-start-1" />
            <StoryCard article={stories[6]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-2 lg:row-start-3" />
            <StoryCard article={stories[7]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-2 lg:row-start-4" />
            <StoryCard article={stories[8]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-2 lg:row-start-5" />

            <StoryCard article={stories[9]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-3 lg:row-start-1" />
            <StoryCard article={stories[10]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-3 lg:row-start-2" />
            <StoryCard article={stories[11]} variant="popularCompact" contentClassName="p-4" className="lg:col-start-3 lg:row-start-3" />
            <StoryCard article={stories[1]} variant="popular" imageClassName="h-44" contentClassName="p-4" className="lg:col-start-3 lg:row-span-2 lg:row-start-4" />
          </div>
        )}

        {newsQuery.hasNextPage && (
          <div className="text-center">
            <button type="button" onClick={() => newsQuery.fetchNextPage()} className="font-ui text-sm font-bold text-slate-400">
              Load More
            </button>
          </div>
        )}

        {stories.length > 4 && (
          <section className="pt-4">
            <h2 className="font-ui text-xl font-bold uppercase">You may be interested</h2>
            <div className="mt-8 grid items-stretch gap-8 md:grid-cols-3">
              <StoryCard article={stories[2]} variant="related" />
              <StoryCard article={stories[3]} variant="related" />
              <StoryCard article={stories[4]} variant="related" />
            </div>
          </section>
        )}

        <CategoryStrip categories={categories} title="Explore more categories" />
        <NewsletterBand />
      </section>
      <BackToTop />
    </>
  );
}
