import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAnalysisContext } from "../context/AnalysisContext";
import { useAnalysis } from "../hooks/useAnalysis";
import { api } from "../api/client";
import EmptyState from "../components/ui/EmptyState";
import Badge from "../components/ui/Badge";
import MarkdownLite from "../components/ui/MarkdownLite";

const GREETING = {
  role: "assistant",
  text: "Ask me anything about your dataset or analysis results — I'll answer only using what's actually been computed.",
};

export default function AIChat() {
  const { analysisId } = useAnalysisContext();
  const { status, results } = useAnalysis(analysisId);
  const navigate = useNavigate();
  const [messages, setMessages] = useState([GREETING]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { setMessages([GREETING]); }, [analysisId]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  if (!analysisId) {
    return <EmptyState title="No analysis available" description="Run an analysis first, then come back to ask questions about it."
                        actionLabel="Go to Upload" onAction={() => window.location.assign("/upload")} />;
  }

  const ml = results?.ml_results;
  const isClustering = results?.problem_type === "clustering";
  const ready = status?.status === "completed";

  const suggestions = isClustering
    ? ["Describe the clusters that were found", "What separates the clusters?", "What patterns exist in this dataset?", "What should I investigate next?"]
    : ["Which model performed best?", "Which features are most important?", "What patterns exist in this dataset?", "What should I investigate next?"];

  const send = async (text) => {
    const message = text ?? input;
    if (!message.trim() || sending) return;
    setMessages((m) => [...m, { role: "user", text: message }]);
    setInput("");
    setSending(true);
    try {
      const res = await api.sendChatMessage(analysisId, message);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, usedLlm: res.used_llm, sources: res.sources }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${e.message}` }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="grid lg:grid-cols-4 gap-6 h-[calc(100vh-8rem)]">
      <div className="lg:col-span-3 card flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm ${
                m.role === "user" ? "bg-primary-600 text-white whitespace-pre-wrap" : "bg-slate-100 dark:bg-slate-800"
              }`}>
                {m.role === "user" ? m.text : <MarkdownLite text={m.text} />}
                {m.role === "assistant" && m.sources && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {m.usedLlm !== undefined && <Badge tone={m.usedLlm ? "success" : "info"}>{m.usedLlm ? "AI-narrated" : "Rule-based"}</Badge>}
                    {m.sources.map((s) => <Badge key={s} tone="pending">{s}</Badge>)}
                  </div>
                )}
              </div>
            </div>
          ))}
          {sending && <div className="text-xs text-slate-400">AI Data Scientist is thinking...</div>}
          <div ref={bottomRef} />
        </div>
        <div className="border-t border-slate-200 dark:border-slate-800 p-3 flex gap-2">
          <input
            className="flex-1 px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent"
            placeholder={ready ? "Ask about your dataset..." : "Waiting for the analysis to finish..."}
            aria-label="Ask a question about your dataset"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button className="btn-primary" onClick={() => send()} disabled={sending}>Send</button>
        </div>
      </div>

      <div className="space-y-4 overflow-y-auto">
        <div className="card p-4">
          <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Active analysis</h4>
          <div className="text-sm space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-medium">Analysis #{analysisId}</span>
              <Badge tone={ready ? "success" : status?.status === "failed" ? "error" : "running"}>{status?.status || "loading"}</Badge>
            </div>
            {results && (
              <>
                <div className="flex justify-between text-xs"><span className="text-slate-500">Problem</span><span className="capitalize">{results.problem_type || "—"}</span></div>
                <div className="flex justify-between text-xs"><span className="text-slate-500">Target</span><span>{results.target_column || "none"}</span></div>
                <div className="flex justify-between text-xs"><span className="text-slate-500">Best model</span><span>{ml?.best_model_name || "—"}</span></div>
              </>
            )}
          </div>
          {isClustering && (
            <div className="mt-3 text-xs rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-800 dark:text-amber-200 p-2.5">
              This analysis has no target column, so there are no prediction metrics. Re-run with a target to get model results.
              <button className="block mt-1.5 underline" onClick={() => navigate("/upload")}>Go to Datasets</button>
            </div>
          )}
        </div>

        <div className="card p-4">
          <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Suggested Questions</h4>
          <div className="space-y-2">
            {suggestions.map((s) => (
              <button key={s} className="w-full text-left text-xs px-3 py-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800"
                      onClick={() => send(s)}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
