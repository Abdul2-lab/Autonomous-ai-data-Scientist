// In development this defaults to the local FastAPI server. For a deployed build,
// set VITE_API_BASE_URL (e.g. in a .env.production file or your host's env vars)
// to your deployed backend's URL, e.g. https://api.yourdomain.com/api
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: options.body instanceof FormData ? undefined : { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res.text();
}

export const api = {
  health: () => request("/health"),

  uploadDataset: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/datasets/upload", { method: "POST", body: form });
  },
  listDatasets: () => request("/datasets"),
  getDataset: (id) => request(`/datasets/${id}`),

  startAnalysis: (datasetId, targetColumn) =>
    request("/analysis", {
      method: "POST",
      body: JSON.stringify({ dataset_id: datasetId, target_column: targetColumn || null }),
    }),
  listAnalyses: () => request("/analysis"),
  getAnalysisStatus: (id) => request(`/analysis/${id}/status`),
  getAnalysisResults: (id) => request(`/analysis/${id}/results`),

  sendChatMessage: (analysisId, message) =>
    request(`/analysis/${analysisId}/chat`, { method: "POST", body: JSON.stringify({ message }) }),

  getReport: (analysisId) => request(`/analysis/${analysisId}/report`, { method: "POST" }),

  // Direct download links (served with Content-Disposition: attachment)
  downloadReportUrl: (analysisId) => `${BASE_URL}/analysis/${analysisId}/report`,
  cleanedDatasetUrl: (analysisId) => `${BASE_URL}/analysis/${analysisId}/cleaned-dataset`,
  exportUrl: (analysisId) => `${BASE_URL}/analysis/${analysisId}/export`,
};
