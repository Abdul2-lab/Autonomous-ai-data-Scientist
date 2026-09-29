import { useAnalysisContext } from "../context/AnalysisContext";
import { useAnalysis } from "../hooks/useAnalysis";
import ChartCard from "../components/charts/ChartCard";
import HistogramChart from "../components/charts/HistogramChart";
import BarChartSimple from "../components/charts/BarChartSimple";
import CorrelationHeatmap from "../components/charts/CorrelationHeatmap";
import ScatterPlot from "../components/charts/ScatterPlot";
import BoxPlotChart from "../components/charts/BoxPlotChart";
import InsightCard from "../components/ui/InsightCard";
import EmptyState from "../components/ui/EmptyState";
import LoadingState from "../components/ui/LoadingState";

export default function EDA() {
  const { analysisId } = useAnalysisContext();
  const { status, results } = useAnalysis(analysisId);

  if (!analysisId) {
    return <EmptyState title="No analysis available" description="Run an analysis first to see EDA results."
                        actionLabel="Go to Upload" onAction={() => window.location.assign("/upload")} />;
  }
  if (!results) return <LoadingState message={`Stage: ${status?.current_stage || "starting"}...`} />;

  const eda = results.eda || {};
  const charts = results.visualizations || [];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold mb-3">Key Insights</h3>
        <div className="grid md:grid-cols-2 gap-3">
          {(eda.findings || []).map((f, i) => <InsightCard key={i} finding={f} />)}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-3">Charts</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {charts.map((c, i) => (
            <ChartCard key={i} title={c.title}>
              {c.type === "histogram" && <HistogramChart bins={c.bins} counts={c.counts} />}
              {c.type === "bar" && <BarChartSimple categories={c.categories} values={c.values} />}
              {c.type === "heatmap" && <CorrelationHeatmap columns={c.columns} matrix={c.matrix} />}
              {c.type === "scatter" && <ScatterPlot points={c.points} />}
              {c.type === "boxplot" && <BoxPlotChart {...c} />}
            </ChartCard>
          ))}
        </div>
      </div>
    </div>
  );
}
