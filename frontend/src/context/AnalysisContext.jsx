import { createContext, useContext, useState } from "react";

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [datasetId, setDatasetId] = useState(() => {
    const v = localStorage.getItem("datasetId");
    return v ? Number(v) : null;
  });
  const [analysisId, setAnalysisId] = useState(() => {
    const v = localStorage.getItem("analysisId");
    return v ? Number(v) : null;
  });

  const selectDataset = (id) => {
    setDatasetId(id);
    localStorage.setItem("datasetId", id);
  };
  const selectAnalysis = (id) => {
    setAnalysisId(id);
    localStorage.setItem("analysisId", id);
  };

  return (
    <AnalysisContext.Provider value={{ datasetId, analysisId, selectDataset, selectAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysisContext() {
  return useContext(AnalysisContext);
}
