import { useRef, useState } from "react";

export default function FileUploader({ onFileSelected, uploading }) {
  const inputRef = useRef();
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = (files) => {
    if (files && files[0]) onFileSelected(files[0]);
  };

  return (
    <div
      className={`card border-2 border-dashed flex flex-col items-center justify-center py-16 px-6 text-center transition-colors ${
        dragOver ? "border-primary-500 bg-primary-50 dark:bg-primary-900/10" : "border-slate-300 dark:border-slate-700"
      }`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
    >
      <div className="text-4xl mb-3">📁</div>
      <h3 className="text-lg font-semibold mb-1">Upload Dataset</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Drag & drop CSV / Excel, or browse your files</p>
      <button className="btn-primary" onClick={() => inputRef.current.click()} disabled={uploading}>
        {uploading ? "Uploading..." : "Browse Files"}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <p className="text-xs text-slate-400 mt-4">Supported: .csv, .xlsx, .xls &middot; Max 50 MB</p>
    </div>
  );
}
