import { useState } from "react";

import Seo, { withBrand } from "../components/Seo";

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  return (
    <section className="max-w-2xl mx-auto">
      <Seo
        title={withBrand("Contact the Editorial Team")}
        description="Contact the FXLFM editorial team about corrections, partnerships, story tips or source information."
        path="/contact"
      />
      <h1 className="font-display text-4xl">Contact Editorial Team</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-300">Send partnerships, corrections, or source tips.</p>
      <form
        className="glass rounded-2xl p-6 mt-6 space-y-4"
        onSubmit={(event) => {
          event.preventDefault();
          setSubmitted(true);
        }}
      >
        <input required className="w-full rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-2 bg-transparent" placeholder="Name" />
        <input type="email" required className="w-full rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-2 bg-transparent" placeholder="Email" />
        <textarea required rows={5} className="w-full rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-2 bg-transparent" placeholder="Message" />
        <button className="bg-brand-700 hover:bg-brand-900 text-white rounded-full px-5 py-2 font-ui" type="submit">Send message</button>
      </form>
      {submitted && <p className="mt-4 text-brand-700 dark:text-brand-300">Thanks. Your message has been captured in this MVP UI flow.</p>}
    </section>
  );
}
