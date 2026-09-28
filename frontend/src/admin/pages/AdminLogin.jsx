import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAdminAuth } from "../AuthContext";

export default function AdminLogin() {
  const { login } = useAdminAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(form.username, form.password);
      navigate("/admin", { replace: true });
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center bg-[#1d282d] px-4 py-12 font-ui text-white">
      <div className="w-full max-w-md">
        <a href="/" className="inline-block font-display text-2xl font-bold text-white">FXLFM</a>
        <div className="mt-5 rounded-[10px] border border-[#455159] bg-[#243136] p-7 shadow-2xl sm:p-9">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#f4ae35]">Editorial desk</p>
          <h1 className="mt-3 font-display text-3xl font-bold">Newsroom sign in</h1>
          <p className="mt-2 text-sm text-slate-400">Use your FXLFM staff account.</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block text-sm">
              <span className="text-slate-300">Username</span>
              <input
                autoFocus
                autoComplete="username"
                value={form.username}
                onChange={(event) => setForm({ ...form, username: event.target.value })}
                className="mt-2 w-full rounded-lg border border-[#606a70] bg-[#1d282d] px-4 py-3 outline-none focus:border-[#f4ae35] focus:ring-2 focus:ring-[#f4ae35]/20"
                required
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-300">Password</span>
              <input
                type="password"
                autoComplete="current-password"
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                className="mt-2 w-full rounded-lg border border-[#606a70] bg-[#1d282d] px-4 py-3 outline-none focus:border-[#f4ae35] focus:ring-2 focus:ring-[#f4ae35]/20"
                required
              />
            </label>
            {error && <p className="rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</p>}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-lg bg-[#f4ae35] px-4 py-3 font-bold text-[#172126] hover:bg-[#ffd075] disabled:opacity-60"
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
