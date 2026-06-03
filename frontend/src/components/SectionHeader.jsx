export default function SectionHeader({ eyebrow, title, action }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
      <div>
        <p className="font-ui uppercase tracking-[0.3em] text-xs text-brand-700 dark:text-brand-200">{eyebrow}</p>
        <h2 className="font-display text-3xl leading-tight">{title}</h2>
      </div>
      {action}
    </div>
  );
}
