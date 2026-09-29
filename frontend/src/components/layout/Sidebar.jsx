import { NavLink } from "react-router-dom";

const ITEMS = [
  { to: "/", label: "Overview", icon: "🏠", end: true },
  { to: "/upload", label: "Datasets", icon: "📁" },
  { to: "/quality", label: "Data Quality", icon: "🧪" },
  { to: "/eda", label: "Exploratory Analysis", icon: "📈" },
  { to: "/ml-lab", label: "ML Lab", icon: "🤖" },
  { to: "/chat", label: "AI Data Scientist", icon: "💬" },
  { to: "/reports", label: "Reports", icon: "📄" },
  { to: "/history", label: "Analysis History", icon: "🕘" },
];

function SidebarContent({ onNavigate }) {
  return (
    <>
      <div className="px-5 py-5 border-b border-slate-200 dark:border-slate-800">
        <h1 className="font-semibold text-sm leading-tight">Autonomous AI<br/>Data Scientist</h1>
      </div>
      <nav className="flex-1 py-3 px-2 space-y-1">
        {ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            title={item.label}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium"
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`
            }
          >
            <span>{item.icon}</span>{item.label}
          </NavLink>
        ))}
      </nav>
    </>
  );
}

export default function Sidebar({ mobileOpen, onClose }) {
  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-60 shrink-0 h-screen sticky top-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-surface-dark flex-col">
        <SidebarContent />
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="absolute inset-0 bg-black/40" onClick={onClose} />
          <aside className="relative w-64 h-full bg-white dark:bg-surface-dark flex flex-col shadow-xl animate-[slideIn_0.15s_ease-out]">
            <SidebarContent onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
