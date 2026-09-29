export function formatNumber(v, digits = 3) {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  if (typeof v !== "number") return String(v);
  if (Math.abs(v) >= 1000) return Math.round(v).toLocaleString();
  return v.toFixed(digits);
}
