import { useEffect, useState } from "react";

import { MoonIcon, SunIcon } from "./DesignPrimitives";

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
      className="grid h-9 w-9 place-items-center rounded-full border-2 border-[#60666b] text-white"
      onClick={() => setEnabled((v) => !v)}
      type="button"
      aria-label={enabled ? "Switch to light mode" : "Switch to dark mode"}
    >
      {enabled ? <SunIcon className="h-4 w-4" /> : <MoonIcon className="h-4 w-4" />}
    </button>
  );
}
