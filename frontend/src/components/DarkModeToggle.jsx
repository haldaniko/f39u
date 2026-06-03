import { useEffect, useState } from "react";

export default function DarkModeToggle() {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const persisted = localStorage.getItem("theme") === "dark";
    setEnabled(persisted);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", enabled);
    localStorage.setItem("theme", enabled ? "dark" : "light");
  }, [enabled]);

  return (
    <button
      className="rounded-full border border-slate-300 dark:border-slate-700 px-3 py-1 text-sm font-ui"
      onClick={() => setEnabled((v) => !v)}
      type="button"
    >
      {enabled ? "Light" : "Dark"}
    </button>
  );
}
