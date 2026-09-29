import { useEffect, useState } from "react";
import { useAnalysisContext } from "../context/AnalysisContext";
import { api } from "../api/client";
import EmptyState from "../components/ui/EmptyState";
import ErrorState from "../components/ui/ErrorState";
import LoadingState from "../components/ui/LoadingState";
import DownloadButtons from "../components/ui/DownloadButtons";

const SECTION_ORDER = [
  "Executive Summary", "Dataset Overview", "Data Quality", "Data Cleaning",
  "Exploratory Analysis", "Important Patterns", "Machine Learning",
  "Model Comparison", "Best Model", "Feature Importance", "AI Insights",
  "Limitations", "Suggested Next Steps",
];

export default function Reports() {
  const { analysisId } = useAnalysisContext();
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!analysisId) { setLoading(false); return; }
    api.getReport(analysisId).then(setReport).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [analysisId]);

  if (!analysisId) {
    return <EmptyState title="No report available" description="Run an analysis to completion first, then a report is generated automatically."
                        actionLabel="Go to Upload" onAction={() => window.location.assign("/upload")} />;
  }
  if (loading) return <LoadingState message="Loading report..." />;
  if (error) return <ErrorState message={error} />;

  const sections = report.content || {};

  return (
    <div className="space-y-6">
      <div className="card p-6 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold">AI Data Science Report</h1>
          <p className="text-xs text-slate-500">Generated {new Date(report.generated_at).toLocaleString()}</p>
        </div>
        <DownloadButtons analysisId={analysisId} report />
      </div>

      {SECTION_ORDER.map((title) => (
        <div key={title} className="card p-5">
          <h3 className="text-sm font-semibold mb-2">{title}</h3>
          <ReportSectionContent value={sections[title]} />
        </div>
      ))}
    </div>
  );
}

function ReportSectionContent({ value }) {
  if (value === null || value === undefined) return <p className="text-sm text-slate-400">No data.</p>;
  if (typeof value === "string") return <p className="text-sm whitespace-pre-wrap">{value}</p>;
  if (Array.isArray(value)) {
    if (value.length === 0) return <p className="text-sm text-slate-400">None.</p>;
    return (
      <ul className="text-sm list-disc list-inside space-y-1">
        {value.map((v, i) => <li key={i}>{typeof v === "object" ? JSON.stringify(v) : String(v)}</li>)}
      </ul>
    );
  }
  return <pre className="text-xs bg-slate-50 dark:bg-slate-900 p-3 rounded-lg overflow-x-auto">{JSON.stringify(value, null, 2)}</pre>;
}
