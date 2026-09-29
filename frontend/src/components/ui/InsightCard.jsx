export default function InsightCard({ finding }) {
  return (
    <div className="card p-4 flex gap-3">
      <span className="text-xl">🔎</span>
      <p className="text-sm">{finding}</p>
    </div>
  );
}
