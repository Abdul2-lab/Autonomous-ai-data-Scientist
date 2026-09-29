export default function ScatterPlot({ points, width = 320, height = 220 }) {
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const xMin = Math.min(...xs), xMax = Math.max(...xs);
  const yMin = Math.min(...ys), yMax = Math.max(...ys);
  const pad = 20;

  const scaleX = (x) => pad + ((x - xMin) / (xMax - xMin || 1)) * (width - pad * 2);
  const scaleY = (y) => height - pad - ((y - yMin) / (yMax - yMin || 1)) * (height - pad * 2);

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
      {points.map((p, i) => (
        <circle key={i} cx={scaleX(p.x)} cy={scaleY(p.y)} r="2.5" className="fill-primary-500" opacity="0.6" />
      ))}
    </svg>
  );
}
