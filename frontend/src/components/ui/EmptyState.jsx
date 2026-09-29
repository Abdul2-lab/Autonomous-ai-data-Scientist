export default function EmptyState({ title, description, actionLabel, onAction }) {
  return (
    <div className="card flex flex-col items-center justify-center text-center py-16 px-6">
      <div className="text-4xl mb-3">📊</div>
      <h3 className="text-lg font-semibold mb-1">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mb-4">{description}</p>
      {actionLabel && (
        <button className="btn-primary" onClick={onAction}>{actionLabel}</button>
      )}
    </div>
  );
}
