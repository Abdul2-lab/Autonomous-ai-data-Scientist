import { useState } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar";
import Topbar from "./components/layout/Topbar";

import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import DataQuality from "./pages/DataQuality";
import EDA from "./pages/EDA";
import MLLab from "./pages/MLLab";
import AIChat from "./pages/AIChat";
import Reports from "./pages/Reports";
import History from "./pages/History";
import Settings from "./pages/Settings";

const TITLES = {
  "/": "Overview",
  "/upload": "Datasets",
  "/quality": "Data Quality",
  "/eda": "Exploratory Analysis",
  "/ml-lab": "ML Lab",
  "/chat": "AI Data Scientist",
  "/reports": "Reports",
  "/history": "Analysis History",
  "/settings": "Settings",
};

export default function App() {
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const title = TITLES[location.pathname] || "Autonomous AI Data Scientist";

  return (
    <div className="flex min-h-screen">
      <Sidebar mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
      <div className="flex-1 min-w-0">
        <Topbar title={title} onMenuClick={() => setMobileNavOpen(true)} />
        <main className="p-4 md:p-6 max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/quality" element={<DataQuality />} />
            <Route path="/eda" element={<EDA />} />
            <Route path="/ml-lab" element={<MLLab />} />
            <Route path="/chat" element={<AIChat />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
