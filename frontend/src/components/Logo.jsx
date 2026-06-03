import { Link } from "react-router-dom";

export default function Logo() {
  return (
    <Link to="/" className="inline-flex items-center gap-3 group">
      <svg
        viewBox="0 0 100 100"
        aria-hidden="true"
        className="h-9 w-9 shrink-0 drop-shadow-sm"
      >
        <defs>
          <linearGradient id="logo-gradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#007f7a" />
            <stop offset="100%" stopColor="#ff6b35" />
          </linearGradient>
        </defs>
        <rect width="100" height="100" rx="22" fill="#0c2f30" />
        <path
          d="M20 70 L40 28 L52 48 L67 20 L80 70"
          fill="none"
          stroke="url(#logo-gradient)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <div>
        <p className="font-display tracking-tight text-2xl leading-none">Facts 39 Unlimited</p>
        <p className="font-ui uppercase text-xs tracking-[0.25em] text-slate-500 dark:text-slate-400">Independent News Desk</p>
      </div>
    </Link>
  );
}
