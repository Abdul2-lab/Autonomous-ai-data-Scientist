import { useEffect, useRef, useState } from "react";
import { useAnalysisContext } from "../context/AnalysisContext";
import { useAnalysis } from "../hooks/useAnalysis";
import { useToast } from "../context/ToastContext";
import { formatNumber } from "../utils/format";
import ProgressStepper from "../components/workflow/ProgressStepper";
import ModelComparisonTable from "../components/ui/ModelComparisonTable";
import ConfusionMatrix from "../components/ui/ConfusionMatrix";
import ClusterResults from "../components/ui/ClusterResults";
import DownloadButtons from "../components/ui/DownloadButtons";
import RocCurve from "../components/charts/RocCurve";
import MetricCard from "../components/ui/MetricCard";
import EmptyState from "../components/ui/EmptyState";
import ErrorState from "../components/ui/ErrorState";
import Badge from "../components/ui/Badge";

const METRIC_LABELS = {
  classification: [["accuracy", "Accuracy"], ["precision", "Precision"], ["recall", "Recall"], ["f1", "F1 score"], ["roc_auc", "ROC-AUC"]],
  regression: [["mae", "MAE"], ["rmse", "RMSE"], ["mse", "MSE"], ["r2", "R²"]],
};

export default function MLLab() {
  const { analysisId } = useAnalysisContext();
  const { status, results, error } = useAnalysis(analysisId);
  const { showToast } = useToast();
  const notified = useRef(false);
  const [selected, setSelected] = useState(null);

  useEffect(() => { notified.current = false; setSelected(null); }, [analysisId]);

  useEffect(() => {
    if (!status || notified.current) return;
    if (status.status === "completed") {
      showToast("Analysis completed successfully.", "success");
      notified.current = true;
    } else if (status.status === "failed") {
      showToast(`Analysis failed: ${status.error_message || "unknown error"}`, "error", 8000);
      notified.current = true;
    }
  }, [status, showToast]);

  if (!analysisId) {
    return <EmptyState title="No analysis running" description="Upload a dataset and run an autonomous analysis first."
                        actionLabel="Go to Upload" onAction={() => window.location.assign("/upload")} />;
  }
  if (error) return <ErrorState message={error} />;

  const ml = results?.ml_results;
  const problemType = ml?.problem_type;
  const selectedName = selected || ml?.best_model_name;
  const selectedExp = ml?.experiments?.find((e) => e.model_name === selectedName);
  const m = selectedExp?.metrics || {};
  const isSupervised = problemType === "classification" || problemType === "regression";

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-4">
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">Pipeline Progress</h3>
            <Badge tone={status?.status === "completed" ? "success" : status?.status === "failed" ? "error" : "running"}>
              {status?.status || "pending"}
            </Badge>
          </div>
          <ProgressStepper currentStage={status?.current_stage} status={status?.status} />
          {status?.error_message && <p className="text-xs text-red-500 mt-3">{status.error_message}</p>}
        </div>

        {status?.status === "completed" && (
          <div className="card p-5">
            <h3 className="text-sm font-semibold mb-3">Downloads</h3>
            <DownloadButtons analysisId={analysisId} report />
          </div>
        )}
      </div>

      <div className="lg:col-span-2 space-y-6 min-w-0">
        {!results ? (
          <div className="card p-6 text-sm text-slate-500">
            {status?.status === "failed" ? "The analysis failed — see the error on the left." : "Waiting for the analysis to complete..."}
          </div>
        ) : (
          <>
            <div className="card p-5">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div><span className="text-slate-500">Problem type</span><div className="font-medium capitalize">{problemType || "—"}</div></div>
                <div><span className="text-slate-500">Target column</span><div className="font-medium">{results.target_column || "None (unsupervised)"}</div></div>
                {isSupervised && <div><span className="text-slate-500">Train / Test rows</span><div className="font-medium">{ml.train_size} / {ml.test_size}</div></div>}
                {isSupervised && <div><span className="text-slate-500">Features used</span><div className="font-medium">{ml.feature_columns?.length}</div></div>}
              </div>
              {ml?.excluded_columns?.length > 0 && (
                <p className="text-xs text-slate-500 mt-3">
                  Excluded from modelling (ID-like / very high-cardinality): {ml.excluded_columns.join(", ")}.
                </p>
              )}
            </div>

            {problemType === "clustering" && (
              <>
                <div className="card p-4 text-sm bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-900/40">
                  No target column was selected, so this run grouped similar rows with clustering instead of training prediction models.
                  To get accuracy / R² and feature importance, run the analysis again with a target column.
                </div>
                <ClusterResults clustering={ml.clustering} />
              </>
            )}

            {problemType === "unsuitable" && (
              <div className="card p-5 text-sm text-slate-600 dark:text-slate-300">{ml?.note || "This dataset is unsuitable for automatic machine learning."}</div>
            )}

            {isSupervised && ml.experiments?.length > 0 && (
              <>
                <div>
                  <h3 className="text-sm font-semibold mb-3">Model Comparison</h3>
                  <ModelComparisonTable problemType={problemType} experiments={ml.experiments}
                                        bestName={ml.best_model_name} selectedName={selectedName} onSelect={setSelected} />
                  <p className="text-xs text-slate-500 mt-2">
                    Best model is chosen by {problemType === "classification" ? "F1 score" : "R²"} on the held-out test set.
                    Other metrics can rank the models differently, so check the ones that matter for your use case.
                  </p>
                </div>

                {selectedExp?.status === "success" && (
                  <div className="card p-5 space-y-5">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold">{selectedExp.model_name} — details</h3>
                      {selectedExp.model_name === ml.best_model_name && <Badge tone="success">Best model</Badge>}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {(METRIC_LABELS[problemType] || []).map(([k, label]) => (
                        <MetricCard key={k} label={label} value={formatNumber(m[k])} />
                      ))}
                    </div>
                    {selectedExp.cross_validation && (
                      <p className="text-xs text-slate-500">
                        Cross-validation ({selectedExp.cross_validation.scoring}): {formatNumber(selectedExp.cross_validation.mean)} ± {formatNumber(selectedExp.cross_validation.std)}
                      </p>
                    )}
                    <div className="grid md:grid-cols-2 gap-6">
                      {m.confusion_matrix && (
                        <div>
                          <h4 className="text-xs font-semibold mb-2 text-slate-500 uppercase">Confusion matrix</h4>
                          <ConfusionMatrix matrix={m.confusion_matrix} labels={m.confusion_matrix_labels} />
                        </div>
                      )}
                      {m.roc_curve && (
                        <div>
                          <h4 className="text-xs font-semibold mb-2 text-slate-500 uppercase">ROC curve</h4>
                          <RocCurve fpr={m.roc_curve.fpr} tpr={m.roc_curve.tpr} auc={m.roc_auc} />
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {selectedExp?.status === "failed" && <ErrorState message={`${selectedExp.model_name} failed to train: ${selectedExp.error}`} />}
              </>
            )}

            {results.explainability?.available && (
              <div className="card p-5">
                <h3 className="text-sm font-semibold mb-1">Feature Importance</h3>
                <p className="text-xs text-slate-500 mb-3">Explains the best model ({ml.best_model_name}) · method: {results.explainability.method}</p>
                <div className="space-y-2">
                  {(() => {
                    const feats = results.explainability.top_features;
                    const max = Math.max(...feats.map((f) => Math.abs(f.importance)), 1e-12);
                    return feats.map((f) => (
                      <div key={f.feature} className="flex items-center gap-3 text-xs">
                        <span className="w-48 truncate" title={f.feature}>{f.feature.replace(/^(numeric|categorical)__/, "")}</span>
                        <div className="flex-1 bg-slate-100 dark:bg-slate-800 rounded h-2">
                          <div className="bg-primary-500 h-2 rounded" style={{ width: `${(Math.abs(f.importance) / max) * 100}%` }} />
                        </div>
                        <span className="w-20 text-right">{formatNumber(f.importance)}</span>
                      </div>
                    ));
                  })()}
                </div>
                <p className="text-[11px] text-slate-500 mt-3">{results.explainability.limitations}</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
