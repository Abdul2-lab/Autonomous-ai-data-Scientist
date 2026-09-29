export default function RocCurve({ fpr, tpr, auc, size = 260 }) {
  const pad = 32;
  const w = size;
  const x = (v) => pad + v * (w - pad * 2);
  const y = (v) => w - pad - v * (w - pad * 2);
  const path = fpr.map((f, i) => `${i === 0 ? "M" : "L"}${x(f)},${y(tpr[i])}`).join(" ");
  const area = `${path} L${x(1)},${y(0)} L${x(0)},${y(0)} Z`;
  return (
    <svg viewBox={`0 0 ${w} ${w}`} width="100%" style={{ maxWidth: size }} className="mx-auto" role="img" aria-label={`ROC curve, AUC ${auc}`}>
      <rect x={pad} y={pad} width={w - pad * 2} height={w - pad * 2} fill="none" className="stroke-slate-300 dark:stroke-slate-700" />
      <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(1)} strokeDasharray="4 4" className="stroke-slate-400" />
      <path d={area} className="fill-primary-500" opacity="0.12" />
      <path d={path} fill="none" className="stroke-primary-600" strokeWidth="2" />
      <text x={w / 2} y={w - 8} textAnchor="middle" fontSize="10" className="fill-slate-500">False positive rate</text>
      <text x="10" y={w / 2} fontSize="10" className="fill-slate-500" transform={`rotate(-90 10 ${w / 2})`} textAnchor="middle">True positive rate</text>
      {auc !== null && auc !== undefined && (
        <text x={x(0.98)} y={y(0.08)} textAnchor="end" fontSize="12" fontWeight="600" className="fill-slate-700 dark:fill-slate-200">AUC = {auc.toFixed(3)}</text>
      )}
    </svg>
  );
}
