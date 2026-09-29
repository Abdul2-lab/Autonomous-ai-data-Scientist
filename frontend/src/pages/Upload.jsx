import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import FileUploader from "../components/ui/FileUploader";
import DataTable from "../components/ui/DataTable";
import LoadingState from "../components/ui/LoadingState";
import ErrorState from "../components/ui/ErrorState";
import Modal from "../components/ui/Modal";
import { useAnalysisContext } from "../context/AnalysisContext";
import { useToast } from "../context/ToastContext";

export default function Upload() {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [target, setTarget] = useState("");
  const [preview, setPreview] = useState(null);
  const [confirmNoTarget, setConfirmNoTarget] = useState(false);
  const { selectDataset, selectAnalysis } = useAnalysisContext();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const loadDatasets = () => {
    setLoading(true);
    api.listDatasets().then(setDatasets).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };

  useEffect(loadDatasets, []);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    try {
      const dataset = await api.uploadDataset(file);
      selectDataset(dataset.id);
      const p = await api.getDataset(dataset.id);
      setPreview(p);
      setTarget("");
      loadDatasets();
      showToast(`"${dataset.original_filename}" uploaded successfully.`, "success");
    } catch (e) {
      setError(e.message);
      showToast(e.message, "error");
    } finally {
      setUploading(false);
    }
  };

  const startAnalysis = async () => {
    if (!preview) return;
    setConfirmNoTarget(false);
    try {
      const analysis = await api.startAnalysis(preview.dataset.id, target || null);
      selectAnalysis(analysis.id);
      showToast(target ? "Autonomous analysis started." : "Clustering analysis started.", "info");
      navigate("/ml-lab");
    } catch (e) {
      setError(e.message);
      showToast(e.message, "error");
    }
  };

  // Running without a target silently switches to unsupervised clustering, so ask first.
  const handleRunClick = () => {
    if (!target) setConfirmNoTarget(true);
    else startAnalysis();
  };

  return (
    <div className="space-y-6">
      <FileUploader onFileSelected={handleUpload} uploading={uploading} />
      {error && <ErrorState message={error} onRetry={() => setError(null)} />}

      {preview && (
        <div className="card p-5 space-y-4">
          <div className="flex flex-wrap gap-6 text-sm">
            <div><span className="text-slate-500">File</span><div className="font-medium">{preview.dataset.original_filename}</div></div>
            <div><span className="text-slate-500">Rows</span><div className="font-medium">{preview.dataset.rows}</div></div>
            <div><span className="text-slate-500">Columns</span><div className="font-medium">{preview.dataset.columns}</div></div>
            <div><span className="text-slate-500">Size</span><div className="font-medium">{(preview.dataset.file_size_bytes / 1024).toFixed(1)} KB</div></div>
          </div>

          <div>
            <label className="text-xs text-slate-500">Target column (optional — leave blank for clustering / auto-detect)</label>
            <select className="mt-1 block w-64 px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent"
                    value={target} onChange={(e) => setTarget(e.target.value)}>
              <option value="">-- None / Auto --</option>
              {preview.columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            {!target ? (
              <p className="text-xs text-amber-600 dark:text-amber-400 mt-1.5 max-w-xl">
                ⚠ No target selected. The app will only group similar rows (clustering) and will NOT train prediction models.
                Pick the column you want to predict (e.g. churned, price) to get accuracy / R², feature importance and a best model.
              </p>
            ) : (
              <p className="text-xs text-slate-500 mt-1.5">Prediction models will be trained to predict “{target}”.</p>
            )}
          </div>

          <DataTable columns={preview.columns} rows={preview.preview_rows} />

          <button className="btn-primary" onClick={handleRunClick}>Run Autonomous Analysis</button>
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold mb-3">Previously Uploaded Datasets</h3>
        {loading ? <LoadingState message="Loading datasets..." /> : (
          datasets.length === 0 ? <p className="text-sm text-slate-500">No datasets uploaded yet.</p> : (
            <div className="grid md:grid-cols-2 gap-3">
              {datasets.map((d) => (
                <div key={d.id} className="card p-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">{d.original_filename}</div>
                    <div className="text-xs text-slate-500">{d.rows} rows &middot; {d.columns} columns &middot; {d.status}</div>
                  </div>
                  <button className="btn-secondary text-xs" onClick={async () => {
                    selectDataset(d.id);
                    setTarget("");
                    setPreview(await api.getDataset(d.id));
                  }}>Select</button>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    
      <Modal
        open={confirmNoTarget}
        title="Run without a target column?"
        onClose={() => setConfirmNoTarget(false)}
        actions={
          <>
            <button className="btn-secondary" onClick={() => setConfirmNoTarget(false)}>Go back &amp; choose a target</button>
            <button className="btn-primary" onClick={startAnalysis}>Run clustering anyway</button>
          </>
        }
      >
        <p>Without a target column no prediction models (classification / regression) will be trained, so you will not get accuracy, R², a best model or feature importance.</p>
        <p>Instead the app will find groups of similar rows using KMeans clustering.</p>
      </Modal>
    </div>
  );
}
