export default function CorrelationHeatmap({ columns, matrix, size = 320 }) {
  const n = columns.length;
  const cell = size / n;

  const colorFor = (v) => {
    if (v === null || v === undefined) return "#e2e8f0";
    const t = (v + 1) / 2; // -1..1 -> 0..1
    const r = Math.round(99 + (239 - 99) * (1 - t));
    const g = Math.round(102 + (68 - 102) * t);
    const b = Math.round(241 - 241 * (1 - t) * 0.3);
    return `rgb(${r},${g},${b})`;
  };

  return (
    <svg width="100%" viewBox={`0 0 ${size + 80} ${size + 20}`}>
      {matrix.map((row, i) =>
        row.map((val, j) => (
          <rect key={`${i}-${j}`} x={j * cell + 80} y={i * cell} width={cell} height={cell}
                fill={colorFor(val)} stroke="#fff" strokeWidth="0.5">
            <title>{`${columns[i]} vs ${columns[j]}: ${val?.toFixed?.(2)}`}</title>
          </rect>
        ))
      )}
      {columns.map((c, i) => (
        <text key={c} x="0" y={i * cell + cell / 1.5} fontSize="9" className="fill-slate-600 dark:fill-slate-300">
          {c.slice(0, 10)}
        </text>
      ))}
    </svg>
  );
}
