import { Link, useParams } from "react-router-dom";

import PageSkeleton from "../components/PageSkeleton";
import Seo, { absoluteUrl, withBrand } from "../components/Seo";
import { useAuthor } from "../hooks/useNewsQuery";

export default function AuthorPage() {
  const { slug } = useParams();
  const { data: author, isLoading } = useAuthor(slug);

  if (isLoading) {
    return <PageSkeleton />;
  }

  if (!author) {
    return (
      <>
        <Seo
          title={withBrand("Author Not Found")}
          description="The requested FXLFM author profile could not be found."
          path={`/author/${slug}`}
          noindex
        />
        <p>Author not found.</p>
      </>
    );
  }

  const socialUrls = [author.x_url, author.linkedin_url, author.instagram_url].filter(Boolean);
  const personSchema = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: author.name,
    url: absoluteUrl(`/author/${author.slug}`),
    jobTitle: author.job_title,
    description: author.bio,
    ...(author.photo_url ? { image: absoluteUrl(author.photo_url) } : {}),
    ...(author.location
      ? { homeLocation: { "@type": "Place", name: author.location } }
      : {}),
    ...(socialUrls.length ? { sameAs: socialUrls } : {}),
  };

  return (
    <>
      <Seo
        title={withBrand(`${author.name}, ${author.job_title}`)}
        description={author.bio}
        path={`/author/${author.slug}`}
        image={author.photo_url}
        structuredData={personSchema}
      />
      <section className="max-w-5xl mx-auto">
        <div className="grid gap-8 md:grid-cols-[220px_1fr] items-start">
          <img
            src={author.photo_url}
            alt={author.name}
            className="w-full aspect-square object-cover rounded-3xl"
          />
          <div>
            <p className="font-ui uppercase text-sm tracking-[0.24em] text-brand-700 dark:text-brand-300">Author</p>
            <h1 className="font-display text-5xl mt-2">{author.name}</h1>
            <p className="text-xl mt-2 text-slate-600 dark:text-slate-300">{author.job_title}</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{author.location}</p>
            {author.joined_at && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Contributor since {author.joined_at}</p>}
            <p className="mt-6 text-lg leading-relaxed">{author.bio}</p>
            <div className="mt-6 flex flex-wrap gap-3">
              {author.x_url && <a href={author.x_url} target="_blank" rel="me noopener" className="glass rounded-full px-4 py-2">X</a>}
              {author.linkedin_url && <a href={author.linkedin_url} target="_blank" rel="me noopener" className="glass rounded-full px-4 py-2">LinkedIn</a>}
              {author.instagram_url && <a href={author.instagram_url} target="_blank" rel="me noopener" className="glass rounded-full px-4 py-2">Instagram</a>}
            </div>
          </div>
        </div>

        <section className="mt-14">
          <h2 className="font-display text-3xl">Latest stories by {author.name}</h2>
          <div className="grid md:grid-cols-2 gap-5 mt-6">
            {(author.articles || []).map((article) => (
              <article key={article.slug} className="glass rounded-2xl p-5">
                <h3 className="font-display text-xl">
                  <Link to={`/article/${article.slug}`}>{article.title}</Link>
                </h3>
                <p className="mt-2 text-slate-600 dark:text-slate-300">{article.summary}</p>
              </article>
            ))}
          </div>
        </section>
      </section>
    </>
  );
}
