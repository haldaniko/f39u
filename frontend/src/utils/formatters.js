export function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function estimateReadingTime(content = "") {
  const words = content.trim().split(/\s+/).filter(Boolean).length;
  const minutes = Math.max(1, Math.ceil(words / 230));
  return `${minutes} min read`;
}
