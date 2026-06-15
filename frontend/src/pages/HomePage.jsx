import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import ArticleCard from "../components/ArticleCard";
import PageSkeleton from "../components/PageSkeleton";
import SectionHeader from "../components/SectionHeader";
import Seo from "../components/Seo";
import { useCategories, useInfiniteNews, useTrending } from "../hooks/useNewsQuery";

export default function HomePage() {
  const newsQuery = useInfiniteNews();
  const trendingQuery = useTrending();
  const categoriesQuery = useCategories();

  const articles = newsQuery.data?.pages.flatMap((page) => page.results || []) || [];
  const categories = Array.isArray(categoriesQuery.data)
    ? categoriesQuery.data
    : categoriesQuery.data?.results || [];
  const hero = articles[0];

  const seo = (
    <Seo
      title="Latest Global News & Breaking Stories | FXLFM"
      description="Read the latest global news, breaking stories and clear reporting across business, technology, politics, science and culture at FXLFM."
      path="/"
      image={hero?.image_url}
    />
  );

  if (newsQuery.isLoading) {
    return <>{seo}<PageSkeleton /></>;
  }

  return (
    <>
      {seo}
      <div className="space-y-10">
        {hero && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-3xl overflow-hidden"
          >
            <img
              src={hero.image_url || "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=1800&q=80"}
              alt={hero.title}
              className="w-full h-64 md:h-[420px] object-cover"
            />
            <div className="p-6 md:p-8">
              <p className="font-ui uppercase tracking-[0.2em] text-brand-700 dark:text-brand-200">Hero Story</p>
              <h1 className="font-display text-4xl md:text-5xl mt-2 max-w-4xl">{hero.title}</h1>
              <p className="mt-3 text-lg text-slate-700 dark:text-slate-300 max-w-3xl">{hero.summary}</p>
              <Link to={`/article/${hero.slug}`} className="inline-block mt-6 bg-accent-500 hover:bg-accent-700 text-white px-5 py-3 rounded-full font-ui">
                Read full story
              </Link>
            </div>
          </motion.section>
        )}

        <section>
        <SectionHeader eyebrow="Live" title="Trending Now" />
        <div className="news-grid">
          {(trendingQuery.data || []).slice(0, 4).map((article, i) => (
            <ArticleCard key={article.slug} article={article} index={i} />
          ))}
        </div>
        </section>

        <section>
        <SectionHeader eyebrow="Topics" title="Categories" />
        <div className="flex flex-wrap gap-3">
          {categories.map((category) => (
            <Link
              key={category.slug}
              to={`/category/${category.slug}`}
              className="glass rounded-full px-4 py-2 font-ui text-sm"
            >
              {category.name}
            </Link>
          ))}
        </div>
        </section>

        <section>
        <SectionHeader eyebrow="Feed" title="Latest News" />
        <div className="news-grid">
          {articles.slice(1).map((article, i) => (
            <ArticleCard key={article.slug} article={article} index={i} />
          ))}
        </div>
        {newsQuery.hasNextPage && (
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => newsQuery.fetchNextPage()}
              className="px-6 py-3 rounded-full bg-brand-700 hover:bg-brand-900 text-white font-ui"
            >
              Load more stories
            </button>
          </div>
        )}
        </section>
      </div>
    </>
  );
}
