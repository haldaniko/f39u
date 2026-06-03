export default function PageSkeleton() {
  return (
    <div className="space-y-4 py-8">
      <div className="h-12 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      <div className="news-grid">
        {Array.from({ length: 6 }).map((_, idx) => (
          <div key={idx} className="h-56 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
        ))}
      </div>
    </div>
  );
}
