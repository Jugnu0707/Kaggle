import { useAppContext } from "../context/AppContext";

export function GlobalLoadingIndicator() {
  const { isLoading } = useAppContext();

  if (!isLoading) {
    return null;
  }

  return (
    <div className="fixed inset-x-0 top-0 z-50">
      <div className="h-1 w-full overflow-hidden bg-slate-200 dark:bg-slate-800">
        <div className="h-full w-1/3 animate-pulse bg-indigo-600" />
      </div>
    </div>
  );
}
