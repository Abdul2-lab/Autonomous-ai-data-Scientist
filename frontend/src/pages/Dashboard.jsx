import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAnalysisContext } from "../context/AnalysisContext";
import Badge from "../components/ui/Badge";
import { api } from "../api/client";
import MetricCard from "../components/ui/MetricCard";
import EmptyState from "../components/ui/EmptyState";

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const navigate = useNavigate();
  const { selectAnalysis, selectDataset } = useAnalysisContext();

  useEffect(() => {
    api.listDatasets().then(setDatasets).catch(() => {});
    api.listAnalyses().then(setAnalyses).catch(() => {});
  }, []);

  const completed = analyses.filter((a) => a.status === "completed").length;

  return (
    <div className="space-y-8">
      <div className="card p-8 bg-gradient-to-br from-primary-600 to-primary-700 text-white border-0">
        <h1 className="text-2xl font-bold mb-2">Your Autonomous AI Data Scientist</h1>
        <p className="text-primary-100 max-w-xl mb-5 text-sm">
          Upload your dataset and let AI discover patterns, build models, and generate actionable insights.
        </p>
        <Link to="/upload" className="inline-block bg-white text-primary-700 px-4 py-2 rounded-xl text-sm font-medium">
          Upload Dataset
        </Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Datasets" value={datasets.length} icon="📁" />
        <MetricCard label="Analyses" value={analyses.length} icon="⚙️" />
        <MetricCard label="Completed" value={completed} icon="✅" />
        <MetricCard label="Models Trained" value={analyses.filter(a => a.problem_type && a.problem_type !== "unsuitable").length} icon="🤖" />
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-3">Recent Analyses</h3>
        {analyses.length === 0 ? (
          <EmptyState title="No analyses yet" description="Upload your first dataset and let your AI Data Scientist analyze it."
                      actionLabel="Upload Dataset" onAction={() => window.location.assign("/upload")} />
        ) : (
          <div className="space-y-2">
            {analyses.slice(0, 5).map((a) => (
              <div key={a.id} className="card p-4 flex items-center justify-between text-sm">
                <div className="flex items-center gap-3">
                  <Badge tone={a.status === "completed" ? "success" : a.status === "failed" ? "error" : "running"}>{a.status}</Badge>
                  <div>
                    <div className="font-medium">Analysis #{a.id} &middot; <span className="capitalize">{a.problem_type || "pending"}</span></div>
                    <div className="text-xs text-slate-500">{a.target_column ? `target: ${a.target_column}` : "no target"}</div>
                  </div>
                </div>
                <button className="btn-secondary text-xs" onClick={() => { selectDataset(a.dataset_id); selectAnalysis(a.id); navigate("/ml-lab"); }}>
                  View
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
