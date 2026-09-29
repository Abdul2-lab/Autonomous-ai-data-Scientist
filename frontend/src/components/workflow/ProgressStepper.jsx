const STAGES = [
  "profiling", "data_quality", "cleaning", "problem_detection", "eda",
  "visualization", "model_selection", "training", "evaluation",
  "explainability", "insight_generation", "report_generation", "completed",
];

const LABELS = {
  profiling: "Dataset Profiler", data_quality: "Data Quality Analysis", cleaning: "Cleaning Data",
  problem_detection: "Detecting ML Problem", eda: "Exploratory Analysis", visualization: "Generating Visualizations",
  model_selection: "Selecting Models", training: "Training Models", evaluation: "Evaluating Models",
  explainability: "Explaining Model", insight_generation: "Generating AI Insights",
  report_generation: "Creating Report", completed: "Completed", queued: "Queued", not_started: "Not Started",
};

export default function ProgressStepper({ currentStage, status }) {
  const currentIndex = STAGES.indexOf(currentStage);

  return (
    <div className="space-y-1">
      {STAGES.map((stage, i) => {
        let state = "pending";
        if (status === "failed" && i === currentIndex) state = "failed";
        else if (i < currentIndex || (stage === "completed" && status === "completed")) state = "done";
        else if (i === currentIndex && status === "running") state = "running";

        const icon = state === "done" ? "✓" : state === "running" ? "⟳" : state === "failed" ? "✕" : "○";
        const color =
          state === "done" ? "text-emerald-500" :
          state === "running" ? "text-primary-500 animate-pulse" :
          state === "failed" ? "text-red-500" : "text-slate-300 dark:text-slate-700";

        return (
          <div key={stage} className="flex items-center gap-3 text-sm py-1">
            <span className={`w-5 text-center font-bold ${color}`}>{icon}</span>
            <span className={state === "pending" ? "text-slate-400" : ""}>{LABELS[stage] || stage}</span>
          </div>
        );
      })}
    </div>
  );
}
