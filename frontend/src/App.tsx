import { useBackendStatus } from "./hooks/useBackendStatus";

function statusLabel(status: "loading" | "healthy" | "unavailable"): string {
  if (status === "loading") {
    return "Checking...";
  }

  if (status === "healthy") {
    return "Healthy";
  }

  return "Unavailable";
}

export default function App() {
  const { status, health } = useBackendStatus();

  return (
    <main className="flex min-h-screen items-center justify-center bg-white px-4">
      <div className="w-full max-w-md text-center">
        <h1 className="text-3xl font-semibold text-gray-900">Oz AI</h1>
        <p className="mt-3 text-base text-gray-600">
          Autonomous Enterprise Incident Response Platform
        </p>

        <div className="mt-10 border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-700">Backend Status</p>
          <p className="mt-2 text-lg text-gray-900">{statusLabel(status)}</p>
          {health && (
            <p className="mt-2 text-sm text-gray-500">
              {health.service} v{health.version}
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
