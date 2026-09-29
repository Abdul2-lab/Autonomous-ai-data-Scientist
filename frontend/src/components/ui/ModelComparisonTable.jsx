import { formatNumber } from "../../utils/format";
import Badge from "./Badge";

const COLUMNS = {
  classification: [
    ["accuracy", "Accuracy"], ["precision", "Precision"], ["recall", "Recall"], ["f1", "F1"], ["roc_auc", "ROC-AUC"],
  ],
  regression: [["mae", "MAE"], ["rmse", "RMSE"], ["r2", "R²"]],
};

export default function ModelComparisonTable({ problemType, experiments, bestName, selectedName, onSelect }) {
  const cols = COLUMNS[problemType] || [];
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
      <table className="table-base">
        <thead>
          <tr>
            <th>Model</th>
            {cols.map(([, label]) => <th key={label}>{label}</th>)}
            <th>CV score</th>
          </tr>
        </thead>
        <tbody>
          {experiments.map((e) => {
            const m = e.metrics || {};
            const isSel = e.model_name === selectedName;
            return (
              <tr
                key={e.model_name}
                tabIndex={0}
                onClick={() => e.status === "success" && onSelect(e.model_name)}
                onKeyDown={(ev) => ev.key === "Enter" && e.status === "success" && onSelect(e.model_name)}
                className={`cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50 ${isSel ? "bg-primary-50 dark:bg-primary-900/20" : ""}`}
              >
                <td className="font-medium whitespace-nowrap">
                  {e.model_name} {e.model_name === bestName && <Badge tone="success">Best</Badge>}
                  {e.status === "failed" && <Badge tone="error">Failed</Badge>}
                </td>
                {cols.map(([key]) => <td key={key}>{e.status === "success" ? formatNumber(m[key]) : "—"}</td>)}
                <td>{e.cross_validation ? formatNumber(e.cross_validation.mean) : "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="text-[11px] text-slate-500 px-3 py-2">Click a row to see that model's details. CV score = cross-validated {problemType === "classification" ? "macro F1" : "R²"} on the training split.</p>
    </div>
  );
}
