/** Stand-in for a page its owning Part has not built yet. */
export default function Placeholder({ title }: { title: string }) {
  return (
    <section>
      <h1>{title}</h1>
      <p className="muted">Coming soon.</p>
    </section>
  );
}
