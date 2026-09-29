export default function ErrorState({ message, onRetry }) {
  return (
    <div className="card p-6 border-red-200 dark:border-red-900/50">
      <div className="flex items-start gap-3">
        <span className="text-2xl">⚠️</span>
        <div className="flex-1">
          <h3 className="font-semibold text-red-700 dark:text-red-400 mb-1">Something went wrong</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">{message}</p>
          {onRetry && (
            <button className="btn-secondary mt-3" onClick={onRetry}>Try Again</button>
          )}
        </div>
      </div>
    </div>
  );
}
