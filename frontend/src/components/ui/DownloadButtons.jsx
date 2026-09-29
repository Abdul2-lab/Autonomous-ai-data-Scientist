import { api } from "../../api/client";

export default function DownloadButtons({ analysisId, cleaned = true, exportJson = true, report = false }) {
  if (!analysisId) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {cleaned && (
        <a className="btn-secondary text-xs" href={api.cleanedDatasetUrl(analysisId)} download>
          ⬇ Cleaned dataset (CSV)
        </a>
      )}
      {exportJson && (
        <a className="btn-secondary text-xs" href={api.exportUrl(analysisId)} download>
          ⬇ Export analysis (JSON)
        </a>
      )}
      {report && (
        <a className="btn-primary text-xs" href={api.downloadReportUrl(analysisId)} target="_blank" rel="noreferrer">
          ⬇ Report (HTML)
        </a>
      )}
    </div>
  );
}
