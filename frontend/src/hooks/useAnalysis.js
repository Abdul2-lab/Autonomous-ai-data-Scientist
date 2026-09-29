import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";

export function useAnalysis(analysisId) {
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    // Always start clean so data from a previously opened analysis never leaks in.
    setStatus(null);
    setResults(null);
    setError(null);
    if (!analysisId) return;
    let cancelled = false;

    const poll = async () => {
      try {
        const s = await api.getAnalysisStatus(analysisId);
        if (cancelled) return;
        setStatus(s);
        if (s.status === "completed" || s.status === "failed") {
          const r = await api.getAnalysisResults(analysisId);
          if (!cancelled) setResults(r);
          clearInterval(intervalRef.current);
        }
      } catch (e) {
        if (!cancelled) setError(e.message);
        clearInterval(intervalRef.current);
      }
    };

    poll();
    intervalRef.current = setInterval(poll, 1500);
    return () => { cancelled = true; clearInterval(intervalRef.current); };
  }, [analysisId]);

  return { status, results, error };
}
