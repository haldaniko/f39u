import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import { formatDate } from "../utils/formatters";

export default function ArticleCard({ article, index = 0 }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.04 }}
      className="glass rounded-2xl overflow-hidden hover:shadow-xl transition-shadow"
    >
      <Link to={`/article/${article.slug}`}>
        <img
          src={article.image_url || "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80"}
          alt={article.title}
          className="h-44 w-full object-cover"
          loading="lazy"
        />
      </Link>
      <div className="p-4">
        <p className="font-ui text-xs uppercase tracking-[0.2em] text-brand-700 dark:text-brand-100">{article.source_name}</p>
        <Link to={`/article/${article.slug}`} className="font-display text-xl leading-tight block mt-2 hover:text-accent-700">
          {article.title}
        </Link>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 line-clamp-3">{article.summary || "No summary yet."}</p>
        <p className="mt-3 font-ui text-xs text-slate-500">{formatDate(article.published_at)}</p>
      </div>
    </motion.article>
  );
}
