import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useTheme } from "../context/ThemeContext";
import Badge from "../components/ui/Badge";

export default function Settings() {
  const [health, setHealth] = useState(null);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => { api.health().then(setHealth).catch(() => {}); }, []);

  return (
    <div className="space-y-6 max-w-xl">
      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-3">Appearance</h3>
        <div className="flex items-center justify-between text-sm">
          <span>Theme</span>
          <button className="btn-secondary" onClick={toggleTheme}>{theme === "dark" ? "Switch to Light" : "Switch to Dark"}</button>
        </div>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold mb-3">Backend Status</h3>
        <div className="flex items-center justify-between text-sm mb-2">
          <span>API</span>
          <Badge tone={health ? "success" : "error"}>{health ? "Connected" : "Unreachable"}</Badge>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span>LLM (AI Chat / Insights)</span>
          <Badge tone={health?.llm_configured ? "success" : "warning"}>
            {health?.llm_configured ? "Configured" : "Not configured"}
          </Badge>
        </div>
        {!health?.llm_configured && (
          <p className="text-xs text-slate-500 mt-2">
            Set <code>OPENAI_API_KEY</code> in <code>backend/.env</code> to enable AI-narrated chat and insights.
            Core data analysis works fully without it.
          </p>
        )}
      </div>
    </div>
  );
}
