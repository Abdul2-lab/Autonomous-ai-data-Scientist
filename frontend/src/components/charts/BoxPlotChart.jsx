export default function BoxPlotChart({ min, q1, median, q3, max, width = 320, height = 90 }) {
  const scale = (v) => pad + ((v - min) / (max - min || 1)) * (width - pad * 2);
  const pad = 20;
  const midY = height / 2;

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
      <line x1={scale(min)} y1={midY} x2={scale(max)} y2={midY} stroke="currentColor" className="text-slate-400" />
      <rect x={scale(q1)} y={midY - 15} width={scale(q3) - scale(q1)} height="30" className="fill-primary-200 stroke-primary-500" strokeWidth="1.5" />
      <line x1={scale(median)} y1={midY - 15} x2={scale(median)} y2={midY + 15} className="stroke-primary-700" strokeWidth="2" />
      <line x1={scale(min)} y1={midY - 8} x2={scale(min)} y2={midY + 8} stroke="currentColor" className="text-slate-400" />
      <line x1={scale(max)} y1={midY - 8} x2={scale(max)} y2={midY + 8} stroke="currentColor" className="text-slate-400" />
    </svg>
  );
}
