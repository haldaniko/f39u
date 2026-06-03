import { Link } from "react-router-dom";

export default function Logo() {
  return (
    <Link to="/" className="inline-flex items-center gap-3 group">
      <span className="h-9 w-9 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 shadow-glow" />
      <div>
        <p className="font-display tracking-tight text-2xl leading-none">Facts 39 Unlimited</p>
        <p className="font-ui uppercase text-xs tracking-[0.25em] text-slate-500 dark:text-slate-400">Independent News Desk</p>
      </div>
    </Link>
  );
}
