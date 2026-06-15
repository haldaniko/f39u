import Seo, { withBrand } from "../components/Seo";

export default function AboutPage() {
  return (
    <section className="max-w-3xl mx-auto space-y-5">
      <Seo
        title={withBrand("About Us")}
        description="Learn about FXLFM, an independent newsroom platform delivering timely global coverage with clear and transparent reporting."
        path="/about"
      />
      <h1 className="font-display text-4xl">About Future Xclusive Local and Foreign Media</h1>
      <p className="text-lg text-slate-700 dark:text-slate-300">
        Future Xclusive Local and Foreign Media is an independent newsroom platform focused on timely global coverage and clear reporting.
      </p>
      <div className="glass rounded-2xl p-6 space-y-3">
        <p><strong>What we do:</strong> collect global stories from trusted public sources and publish them in one place.</p>
        <p><strong>Editorial pledge:</strong> preserve facts, provide context, and keep reporting clear and transparent.</p>
      </div>
    </section>
  );
}
