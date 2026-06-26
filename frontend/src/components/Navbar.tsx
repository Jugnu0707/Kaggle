import { useAppContext } from "../context/AppContext";

function StatusIndicator({ status }: { status: "loading" | "healthy" | "unavailable" }) {
  const styles = {
    loading: "bg-yellow-400",
    healthy: "bg-green-500",
    unavailable: "bg-red-500",
  };
  const labels = {
    loading: "Checking backend...",
    healthy: "Backend online",
    unavailable: "Backend unavailable",
  };

  return (
    <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
      <span className={`h-2.5 w-2.5 rounded-full ${styles[status]}`} />
      <span>{labels[status]}</span>
    </div>
  );
}

export function Navbar() {
  const { backendStatus, health } = useAppContext();

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
          Oz
        </div>
        <div>
          <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Oz AI</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Autonomous Enterprise Incident Response
          </p>
        </div>
      </div>
      <div className="text-right">
        <StatusIndicator status={backendStatus} />
        {health && (
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {health.application_name} v{health.version}
          </p>
        )}
      </div>
    </header>
  );
}
