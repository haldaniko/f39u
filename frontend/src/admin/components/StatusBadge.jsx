const styles = {
  published: "bg-emerald-100 text-emerald-800 dark:bg-emerald-400/15 dark:text-emerald-300",
  pending_review: "bg-amber-100 text-amber-800 dark:bg-amber-400/15 dark:text-amber-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-400/15 dark:text-red-300",
  rewritten: "bg-blue-100 text-blue-800 dark:bg-blue-400/15 dark:text-blue-300",
  draft: "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-200",
};

const labels = {
  published: "Опубликовано",
  pending_review: "На проверке",
  rejected: "Отклонено",
  rewritten: "Переписано",
  draft: "Черновик",
};

export function formatStatus(status) {
  return labels[status] || "Неизвестно";
}

export default function StatusBadge({ status }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${styles[status] || styles.draft}`}>
      {formatStatus(status)}
    </span>
  );
}
