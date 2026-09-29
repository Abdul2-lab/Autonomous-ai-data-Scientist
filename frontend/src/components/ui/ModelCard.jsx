import Badge from "./Badge";

export default function ModelCard({ experiment, isBest }) {
  const m = experiment.metrics || {};
  return (
    <div className={`card p-4 ${isBest ? "border-primary-500 border-2" : ""}`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-sm">{experiment.model_name}</h4>
        {isBest && <Badge tone="success">Best Model</Badge>}
        {experiment.status === "failed" && <Badge tone="error">Failed</Badge>}
      </div>
      {experiment.status === "success" ? (
        <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-400">
          {Object.entries(m).filter(([k]) => !["confusion_matrix", "confusion_matrix_labels", "primary_metric"].includes(k)).map(([k, v]) => (
            v !== null && v !== undefined && typeof v !== "object" ? (
              <div key={k} className="flex justify-between">
                <span className="capitalize">{k.replace(/_/g, " ")}</span>
                <span className="font-medium text-slate-900 dark:text-slate-100">{typeof v === "number" ? v.toFixed(3) : String(v)}</span>
              </div>
            ) : null
          ))}
        </div>
      ) : (
        <p className="text-xs text-red-500">{experiment.error}</p>
      )}
    </div>
  );
}
