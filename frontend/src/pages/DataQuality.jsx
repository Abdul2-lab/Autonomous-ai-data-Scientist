import { useAnalysisContext } from "../context/AnalysisContext";
import { useAnalysis } from "../hooks/useAnalysis";
import MetricCard from "../components/ui/MetricCard";
import EmptyState from "../components/ui/EmptyState";
import LoadingState from "../components/ui/LoadingState";
import DownloadButtons from "../components/ui/DownloadButtons";

export default function DataQuality() {
  const { analysisId } = useAnalysisContext();
  const { status, results } = useAnalysis(analysisId);

  if (!analysisId) {
    return <EmptyState title="No analysis available" description="Run an analysis first to see data-quality findings."
                        actionLabel="Go to Upload" onAction={() => window.location.assign("/upload")} />;
  }
  if (!results) return <LoadingState message={`Stage: ${status?.current_stage || "starting"}...`} />;

  const q = results.quality || {};
  const cleaning = results.cleaning || {};

  return (
    <div className="space-y-6">
      <div className="card p-6 flex items-center gap-6">
        <div className="text-4xl font-bold text-primary-600">{q.quality_score ?? "—"}</div>
        <div>
          <h3 className="font-semibold text-sm">Overall Data Quality Score</h3>
          <p className="text-xs text-slate-500">Out of 100, based on missing values, duplicates, and structural issues.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Duplicate Rows" value={q.duplicate_rows ?? 0} />
        <MetricCard label="Constant Columns" value={(q.constant_columns || []).length} />
        <MetricCard label="Duplicate Columns" value={(q.duplicate_columns || []).length} />
        <MetricCard label="High-Cardinality Cols" value={(q.high_cardinality_columns || []).length} />
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-3">Missing Values (original data)</h3>
        <div className="space-y-2">
          {(() => {
            const totalRows = results.profiling?.rows || cleaning.original_rows || 1;
            const entries = Object.entries(q.missing_values || {}).filter(([, v]) => v > 0);
            if (entries.length === 0) return <p className="text-sm text-slate-500">No missing values detected.</p>;
            return entries.map(([col, v]) => {
              const pct = (v / totalRows) * 100;
              return (
                <div key={col} className="flex items-center gap-3 text-xs">
                  <span className="w-40 truncate" title={col}>{col}</span>
                  <div className="flex-1 bg-slate-100 dark:bg-slate-800 rounded h-2">
                    <div className="bg-amber-500 h-2 rounded" style={{ width: `${Math.min(100, pct)}%` }} />
                  </div>
                  <span className="w-28 text-right">{v} ({pct.toFixed(1)}%)</span>
                </div>
              );
            });
          })()}
        </div>
      </div>

      <div className="card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h3 className="text-sm font-semibold">Before vs after cleaning</h3>
          {cleaning.cleaned_dataset_available && <DownloadButtons analysisId={analysisId} exportJson={false} />}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div><span className="text-slate-500">Rows</span><div className="font-medium">{cleaning.original_rows} → {cleaning.cleaned_rows}</div></div>
          <div><span className="text-slate-500">Columns</span><div className="font-medium">{cleaning.original_columns} → {cleaning.cleaned_columns}</div></div>
          <div><span className="text-slate-500">Missing values</span><div className="font-medium">{cleaning.missing_values_before} → {cleaning.missing_values_after}</div></div>
          <div><span className="text-slate-500">Duplicates removed</span><div className="font-medium">{cleaning.duplicate_rows_removed}</div></div>
        </div>
        <p className="text-xs text-slate-500 mt-3">Your original upload is never modified. The cleaned dataset is a separate copy you can download.</p>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-3">Cleaning Actions Taken</h3>
        <ul className="text-sm list-disc list-inside space-y-1 text-slate-600 dark:text-slate-400">
          {(cleaning.actions_taken || []).map((a, i) => <li key={i}>{a}</li>)}
        </ul>
      </div>

      {Object.keys(cleaning.outlier_report || {}).length > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-semibold mb-3">Outliers Detected (IQR method)</h3>
          <table className="table-base">
            <thead><tr><th>Column</th><th>Count</th><th>% of rows</th></tr></thead>
            <tbody>
              {Object.entries(cleaning.outlier_report).map(([col, info]) => (
                <tr key={col}><td>{col}</td><td>{info.count}</td><td>{info.percentage}%</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
