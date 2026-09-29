import ChartCard from "../charts/ChartCard";
import BarChartSimple from "../charts/BarChartSimple";
import ClusterScatter, { CLUSTER_COLORS } from "../charts/ClusterScatter";
import { formatNumber } from "../../utils/format";

function silhouetteLabel(s) {
  if (s === null || s === undefined) return ["Unknown", "text-slate-500"];
  if (s >= 0.5) return ["Well separated", "text-emerald-600"];
  if (s >= 0.25) return ["Weak but usable structure", "text-amber-600"];
  return ["Little real cluster structure", "text-red-500"];
}

export default function ClusterResults({ clustering }) {
  if (!clustering?.available) {
    return <div className="card p-5 text-sm text-slate-500">{clustering?.reason || "Clustering was not available for this dataset."}</div>;
  }
  const [label, tone] = silhouetteLabel(clustering.silhouette);
  const numericCols = clustering.features_used.filter((f) => clustering.clusters[0].numeric_means[f] !== undefined);
  const catCols = Object.keys(clustering.clusters[0].categorical_top || {});

  return (
    <div className="space-y-6">
      <div className="card p-5 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div><span className="text-slate-500">Algorithm</span><div className="font-medium">{clustering.algorithm}</div></div>
        <div><span className="text-slate-500">Clusters found</span><div className="font-medium">{clustering.best_k}</div></div>
        <div><span className="text-slate-500">Silhouette</span><div className="font-medium">{formatNumber(clustering.silhouette)}</div></div>
        <div><span className="text-slate-500">Quality</span><div className={`font-medium ${tone}`}>{label}</div></div>
      </div>
      <p className="text-xs text-slate-500 -mt-3">{clustering.interpretation} The number of clusters was chosen automatically by trying k = 2 … {Math.max(...clustering.k_scores.map((k) => k.k))} and keeping the best silhouette score.</p>

      <div className="grid md:grid-cols-2 gap-4">
        <ChartCard title="Clusters (2-D projection)">
          <ClusterScatter points={clustering.pca_points} />
          <div className="flex flex-wrap gap-3 mt-2 text-xs">
            {clustering.clusters.map((c) => (
              <span key={c.cluster} className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: CLUSTER_COLORS[c.cluster % CLUSTER_COLORS.length] }} />
                Cluster {c.cluster}
              </span>
            ))}
          </div>
        </ChartCard>
        <ChartCard title="Cluster sizes (rows)">
          <BarChartSimple categories={clustering.clusters.map((c) => `Cluster ${c.cluster}`)} values={clustering.clusters.map((c) => c.size)} />
        </ChartCard>
      </div>

      {clustering.distinguishing_features?.length > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-semibold mb-2">What separates the clusters</h3>
          <p className="text-xs text-slate-500 mb-3">Numeric features whose average differs most between clusters (in standard deviations).</p>
          <div className="space-y-2">
            {clustering.distinguishing_features.map((d) => (
              <div key={d.feature} className="flex items-center gap-3 text-xs">
                <span className="w-40 truncate">{d.feature}</span>
                <div className="flex-1 bg-slate-100 dark:bg-slate-800 rounded h-2">
                  <div className="bg-primary-500 h-2 rounded" style={{ width: `${Math.min(100, d.separation * 50)}%` }} />
                </div>
                <span className="w-12 text-right">{d.separation.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-3">Cluster profiles</h3>
        <div className="overflow-x-auto">
          <table className="table-base">
            <thead>
              <tr>
                <th>Cluster</th><th>Rows</th><th>Share</th>
                {numericCols.map((c) => <th key={c}>avg {c}</th>)}
                {catCols.map((c) => <th key={c}>top {c}</th>)}
              </tr>
            </thead>
            <tbody>
              {clustering.clusters.map((cl) => (
                <tr key={cl.cluster}>
                  <td className="font-medium">
                    <span className="inline-block w-2.5 h-2.5 rounded-full mr-2" style={{ background: CLUSTER_COLORS[cl.cluster % CLUSTER_COLORS.length] }} />
                    {cl.cluster}
                  </td>
                  <td>{cl.size}</td>
                  <td>{(cl.share * 100).toFixed(1)}%</td>
                  {numericCols.map((c) => <td key={c}>{formatNumber(cl.numeric_means[c], 2)}</td>)}
                  {catCols.map((c) => (
                    <td key={c}>{cl.categorical_top[c] ? `${cl.categorical_top[c].top_value} (${(cl.categorical_top[c].share * 100).toFixed(0)}%)` : "—"}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-3">Silhouette score by number of clusters</h3>
        <table className="table-base">
          <thead><tr><th>k</th><th>Silhouette</th><th>Inertia</th></tr></thead>
          <tbody>
            {clustering.k_scores.map((k) => (
              <tr key={k.k} className={k.k === clustering.best_k ? "bg-primary-50 dark:bg-primary-900/20 font-medium" : ""}>
                <td>{k.k}{k.k === clustering.best_k ? " (selected)" : ""}</td><td>{formatNumber(k.silhouette)}</td><td>{formatNumber(k.inertia, 1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
