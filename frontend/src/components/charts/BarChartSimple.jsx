export default function BarChartSimple({ categories, values, width = 320, height = 180 }) {
  const max = Math.max(...values, 1);
  const barHeight = (height - 20) / categories.length;
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
      {categories.map((cat, i) => {
        const w = (values[i] / max) * (width - 100);
        return (
          <g key={cat} transform={`translate(0, ${i * barHeight})`}>
            <text x="0" y={barHeight / 2 + 4} fontSize="10" className="fill-slate-600 dark:fill-slate-300">
              {String(cat).slice(0, 12)}
            </text>
            <rect x="90" y={barHeight * 0.15} width={w} height={barHeight * 0.7} className="fill-primary-500" rx="3" />
            <text x={95 + w} y={barHeight / 2 + 4} fontSize="9" className="fill-slate-500">{values[i]}</text>
          </g>
        );
      })}
    </svg>
  );
}
