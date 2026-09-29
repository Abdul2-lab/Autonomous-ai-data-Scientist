export const CLUSTER_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7", "#84cc16", "#ec4899"];

export default function ClusterScatter({ points, width = 480, height = 300 }) {
  if (!points || points.length === 0) return null;
  const xs = points.map((p) => p.x), ys = points.map((p) => p.y);
  const xMin = Math.min(...xs), xMax = Math.max(...xs), yMin = Math.min(...ys), yMax = Math.max(...ys);
  const pad = 24;
  const sx = (v) => pad + ((v - xMin) / (xMax - xMin || 1)) * (width - pad * 2);
  const sy = (v) => height - pad - ((v - yMin) / (yMax - yMin || 1)) * (height - pad * 2);
  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label="2D projection of clusters">
      <rect x="0" y="0" width={width} height={height} rx="8" className="fill-slate-50 dark:fill-slate-900/40" />
      {points.map((p, i) => (
        <circle key={i} cx={sx(p.x)} cy={sy(p.y)} r="3.2" fill={CLUSTER_COLORS[p.cluster % CLUSTER_COLORS.length]} opacity="0.75" />
      ))}
      <text x={width / 2} y={height - 6} textAnchor="middle" fontSize="10" className="fill-slate-500">Principal component 1</text>
      <text x="10" y={height / 2} fontSize="10" className="fill-slate-500" transform={`rotate(-90 10 ${height / 2})`} textAnchor="middle">Principal component 2</text>
    </svg>
  );
}
