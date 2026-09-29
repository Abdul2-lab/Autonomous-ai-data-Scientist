import { useEffect } from "react";

export default function Modal({ open, title, children, onClose, actions }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label={title}>
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative card w-full max-w-md p-6 animate-[fadeIn_0.15s_ease-out]">
        <h3 className="text-base font-semibold mb-2">{title}</h3>
        <div className="text-sm text-slate-600 dark:text-slate-300 space-y-2">{children}</div>
        <div className="flex justify-end gap-2 mt-5">{actions}</div>
      </div>
    </div>
  );
}
