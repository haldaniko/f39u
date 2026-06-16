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
    <div className="min-h-screen bg-slate-950 px-4 py-12 font-ui text-white grid place-items-center">
      <div className="w-full max-w-md">
        <a href="/" className="inline-block text-sm text-teal-300">FXLFM / Back to site</a>
        <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.06] p-7 shadow-2xl sm:p-9">
          <p className="text-xs uppercase tracking-[0.28em] text-teal-300">Newsroom access</p>
          <h1 className="mt-3 text-3xl font-semibold">Welcome back</h1>
          <p className="mt-2 text-sm text-slate-400">Sign in with a Django staff account.</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block text-sm">
              <span className="text-slate-300">Username</span>
              <input
                autoFocus
                autoComplete="username"
                value={form.username}
                onChange={(event) => setForm({ ...form, username: event.target.value })}
                className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 outline-none focus:border-teal-400"
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
                className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 outline-none focus:border-teal-400"
                required
              />
            </label>
            {error && <p className="rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</p>}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-xl bg-teal-400 px-4 py-3 font-semibold text-slate-950 hover:bg-teal-300 disabled:opacity-60"
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
