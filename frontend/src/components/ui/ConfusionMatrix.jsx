export default function ConfusionMatrix({ matrix, labels }) {
  if (!matrix || matrix.length === 0) return null;
  const max = Math.max(...matrix.flat(), 1);
  return (
    <div className="overflow-x-auto">
      <table className="text-xs border-separate border-spacing-1 mx-auto">
        <thead>
          <tr>
            <th />
            <th colSpan={labels.length} className="text-slate-500 font-medium pb-1">Predicted</th>
          </tr>
          <tr>
            <th />
            {labels.map((l) => <th key={l} className="px-3 py-1 font-semibold">{l}</th>)}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <th className="pr-2 text-right font-semibold whitespace-nowrap">
                {i === 0 && <span className="block text-[10px] text-slate-500 font-medium">Actual</span>}
                {labels[i]}
              </th>
              {row.map((v, j) => {
                const intensity = v / max;
                const correct = i === j;
                return (
                  <td
                    key={j}
                    title={`Actual ${labels[i]}, predicted ${labels[j]}: ${v}`}
                    className={`w-20 h-14 text-center rounded-lg font-semibold ${correct ? "text-white" : "text-slate-900 dark:text-slate-100"}`}
                    style={{
                      background: correct
                        ? `rgba(79,70,229,${0.25 + 0.75 * intensity})`
                        : `rgba(239,68,68,${0.08 + 0.6 * intensity})`,
                    }}
                  >
                    {v}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-[11px] text-slate-500 text-center mt-2">Blue diagonal = correct predictions, red = mistakes.</p>
    </div>
  );
}
