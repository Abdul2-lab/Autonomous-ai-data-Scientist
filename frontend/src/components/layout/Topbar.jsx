import { useTheme } from "../../context/ThemeContext";

export default function Topbar({ title, onMenuClick }) {
  const { theme, toggleTheme } = useTheme();
  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 md:px-6 bg-white/80 dark:bg-surface-dark/80 backdrop-blur sticky top-0 z-10">
      <div className="flex items-center gap-3 min-w-0">
        <button
          className="md:hidden text-lg px-1 -ml-1"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
        >
          ☰
        </button>
        <nav aria-label="Breadcrumb" className="text-sm truncate">
          <span className="text-slate-400 dark:text-slate-500">Autonomous AI Data Scientist</span>
          <span className="text-slate-400 dark:text-slate-500 mx-1.5">/</span>
          <span className="font-semibold">{title}</span>
        </nav>
      </div>
      <button onClick={toggleTheme} className="btn-secondary px-3 py-1.5 text-xs shrink-0" title="Toggle color theme">
        {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
      </button>
    </header>
  );
}
