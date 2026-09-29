export default function ChartCard({ title, children }) {
  return (
    <div className="card p-4">
      <h4 className="text-sm font-semibold mb-3">{title}</h4>
      {children}
    </div>
  );
}
