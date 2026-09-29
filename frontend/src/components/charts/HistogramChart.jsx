export default function HistogramChart({ bins, counts, width = 320, height = 160 }) {
  const max = Math.max(...counts, 1);
  const barWidth = width / counts.length;
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} className="text-primary-500">
      {counts.map((c, i) => {
        const h = (c / max) * (height - 20);
        return (
          <rect key={i} x={i * barWidth + 1} y={height - h - 15} width={barWidth - 2} height={h}
                fill="currentColor" opacity="0.85" rx="2" />
        );
      })}
      <text x="0" y={height - 2} fontSize="9" fill="currentColor" opacity="0.6">
        {bins[0]?.toFixed(1)} - {bins[bins.length - 1]?.toFixed(1)}
      </text>
    </svg>
  );
}
