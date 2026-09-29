import { createContext, useCallback, useContext, useState } from "react";

const ToastContext = createContext(null);
let idCounter = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((t) => t.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback((message, tone = "info", duration = 4000) => {
    const id = ++idCounter;
    setToasts((t) => [...t, { id, message, tone }]);
    if (duration > 0) setTimeout(() => dismiss(id), duration);
    return id;
  }, [dismiss]);

  return (
    <ToastContext.Provider value={{ showToast, dismiss }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 space-y-2 w-80 max-w-[90vw]">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`rounded-xl shadow-lg px-4 py-3 text-sm text-white flex items-start justify-between gap-3 animate-[fadeIn_0.15s_ease-out] ${
              t.tone === "success" ? "bg-emerald-600" :
              t.tone === "error" ? "bg-red-600" :
              t.tone === "warning" ? "bg-amber-600" : "bg-slate-800"
            }`}
          >
            <span>{t.message}</span>
            <button onClick={() => dismiss(t.id)} className="opacity-70 hover:opacity-100">✕</button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
