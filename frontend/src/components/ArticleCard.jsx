import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import { estimateReadingTime, formatDate } from "../utils/formatters";

export default function ArticleCard({ article, index = 0 }) {
  const readTime = estimateReadingTime(article.rewritten_content || article.summary || article.title);

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.04 }}
      className="news-card group overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200 transition duration-200 hover:-translate-y-1 hover:shadow-xl dark:bg-slate-900 dark:ring-slate-800"
    >
      <Link to={`/article/${article.slug}`}>
        <img
          src={article.image_url || "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80"}
          alt={article.title}
          className="h-44 w-full object-cover transition duration-300 group-hover:scale-105"
          loading="lazy"
        />
      </Link>
      <div className="p-4">
        <p className="font-ui text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">
          {article.source_name || article.category?.name || "FXLFM"}
        </p>
        <Link to={`/article/${article.slug}`} className="mt-2 block font-body text-xl font-semibold leading-tight hover:text-accent-700">
          {article.title}
        </Link>
        <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
          {article.summary || "No summary yet."}
        </p>
        <div className="mt-4 flex items-center justify-between gap-3 font-ui text-[11px] font-bold uppercase tracking-[0.08em]">
          <span className="rounded-sm bg-red-500 px-2 py-1 text-white">Breaking News</span>
          <span className="text-slate-500">{readTime}</span>
        </div>
        <p className="mt-3 font-ui text-xs text-slate-500">{formatDate(article.published_at)}</p>
      </div>
    </motion.article>
  );
}
