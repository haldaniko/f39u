import { Link } from "react-router-dom";

export default function Logo() {
  return (
    <Link to="/" className="group inline-flex items-center gap-3">
      <div>
        <p className="font-display text-2xl font-bold uppercase leading-none tracking-normal text-white">FXLMF</p>
      </div>
    </Link>
  );
}
