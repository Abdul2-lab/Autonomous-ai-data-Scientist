import { useMemo, useState } from "react";

export default function DataTable({ columns, rows, pageSize = 10 }) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    if (!search) return rows;
    const q = search.toLowerCase();
    return rows.filter((row) => columns.some((c) => String(row[c] ?? "").toLowerCase().includes(q)));
  }, [rows, search, columns]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageRows = filtered.slice(page * pageSize, page * pageSize + pageSize);

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <input
          className="px-3 py-1.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent w-56"
          placeholder="Search rows..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
        />
        <span className="text-xs text-slate-500">{filtered.length} rows</span>
      </div>
      <div className="overflow-x-auto max-h-96 overflow-y-auto rounded-lg border border-slate-200 dark:border-slate-800">
        <table className="table-base">
          <thead><tr>{columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>
            {pageRows.map((row, i) => (
              <tr key={i}>{columns.map((c) => <td key={c}>{String(row[c] ?? "")}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-end gap-2 mt-3 text-sm">
        <button className="btn-secondary px-2 py-1" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>Prev</button>
        <span className="text-slate-500">Page {page + 1} / {totalPages}</span>
        <button className="btn-secondary px-2 py-1" disabled={page >= totalPages - 1} onClick={() => setPage((p) => p + 1)}>Next</button>
      </div>
    </div>
  );
}
