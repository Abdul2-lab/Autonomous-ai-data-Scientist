// Small, dependency-free renderer for the subset of Markdown chat answers use:
// **bold**, `code`, headings, bullet/numbered lists and simple tables.
function inline(text, keyPrefix = "") {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={keyPrefix + i}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={keyPrefix + i} className="px-1 rounded bg-black/10 dark:bg-white/10 text-[0.85em]">{part.slice(1, -1)}</code>;
    return <span key={keyPrefix + i}>{part}</span>;
  });
}

const isTableRow = (l) => l.trim().startsWith("|") && l.trim().endsWith("|");
const isSeparator = (l) => /^\s*\|?[\s:|-]+\|?\s*$/.test(l) && l.includes("-");

export default function MarkdownLite({ text }) {
  const lines = String(text || "").split("\n");
  const blocks = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }

    if (isTableRow(line)) {
      const rows = [];
      while (i < lines.length && isTableRow(lines[i])) { rows.push(lines[i]); i++; }
      const cells = rows.filter((r) => !isSeparator(r)).map((r) => r.trim().slice(1, -1).split("|").map((c) => c.trim()));
      const [head, ...body] = cells;
      blocks.push(
        <div key={blocks.length} className="overflow-x-auto my-2">
          <table className="text-xs border-collapse">
            <thead><tr>{head.map((c, j) => <th key={j} className="text-left px-2 py-1 border-b border-slate-300 dark:border-slate-600">{inline(c)}</th>)}</tr></thead>
            <tbody>{body.map((r, k) => <tr key={k}>{r.map((c, j) => <td key={j} className="px-2 py-1 border-b border-slate-200 dark:border-slate-700">{inline(c)}</td>)}</tr>)}</tbody>
          </table>
        </div>
      );
      continue;
    }

    if (/^\s*([-*•])\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*([-*•])\s+/.test(lines[i])) { items.push(lines[i].replace(/^\s*([-*•])\s+/, "")); i++; }
      blocks.push(<ul key={blocks.length} className="list-disc pl-5 my-1 space-y-0.5">{items.map((t, j) => <li key={j}>{inline(t)}</li>)}</ul>);
      continue;
    }

    if (/^\s*\d+[.)]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) { items.push(lines[i].replace(/^\s*\d+[.)]\s+/, "")); i++; }
      blocks.push(<ol key={blocks.length} className="list-decimal pl-5 my-1 space-y-0.5">{items.map((t, j) => <li key={j}>{inline(t)}</li>)}</ol>);
      continue;
    }

    const heading = line.match(/^#{1,4}\s+(.*)$/);
    if (heading) { blocks.push(<p key={blocks.length} className="font-semibold mt-2">{inline(heading[1])}</p>); i++; continue; }

    blocks.push(<p key={blocks.length} className="my-1">{inline(line)}</p>);
    i++;
  }
  return <div>{blocks}</div>;
}
