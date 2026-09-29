import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAnalysisContext } from "../context/AnalysisContext";
import { useNavigate } from "react-router-dom";
import Badge from "../components/ui/Badge";
import EmptyState from "../components/ui/EmptyState";
import LoadingState from "../components/ui/LoadingState";

const STATUS_TONE = { completed: "success", running: "running", pending: "pending", failed: "error" };

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const { selectAnalysis, selectDataset } = useAnalysisContext();
  const navigate = useNavigate();

  useEffect(() => {
    api.listAnalyses().then(setAnalyses).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState message="Loading history..." />;
  if (analyses.length === 0) {
    return <EmptyState title="No analyses yet" description="Your past analyses will appear here once you run one."
                        actionLabel="Upload Dataset" onAction={() => navigate("/upload")} />;
  }

  return (
    <div className="space-y-3">
      {analyses.map((a) => (
        <div key={a.id} className="card p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Badge tone={STATUS_TONE[a.status] || "pending"}>{a.status}</Badge>
            <div>
              <div className="text-sm font-medium">Analysis #{a.id} &middot; Dataset #{a.dataset_id}</div>
              <div className="text-xs text-slate-500">
                {a.problem_type || "pending"} {a.target_column ? `→ target: ${a.target_column}` : ""} &middot;{" "}
                {new Date(a.created_at).toLocaleString()}
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn-secondary text-xs" onClick={() => { selectDataset(a.dataset_id); selectAnalysis(a.id); navigate("/ml-lab"); }}>
              View
            </button>
            <button className="btn-secondary text-xs" onClick={() => { selectAnalysis(a.id); navigate("/reports"); }}>
              Report
            </button>
            {a.status === "completed" && (
              <a className="btn-secondary text-xs" href={api.cleanedDatasetUrl(a.id)} download>Cleaned CSV</a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
