import { useAppContext } from "../context/AppContext";

export function BackendUnavailableBanner() {
  const { backendStatus } = useAppContext();

  if (backendStatus === "healthy") {
    return null;
  }

  const message =
    backendStatus === "loading"
      ? "Checking backend connection..."
      : "Backend unavailable. Some data may be outdated or missing. Please ensure the API server is running.";

  return (
    <div
      role="status"
      className={`border-b px-6 py-3 text-sm ${
        backendStatus === "loading"
          ? "border-yellow-200 bg-yellow-50 text-yellow-900 dark:border-yellow-900 dark:bg-yellow-950/40 dark:text-yellow-200"
          : "border-red-200 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200"
      }`}
    >
      {message}
    </div>
  );
}
