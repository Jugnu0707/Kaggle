import { useEffect, useState } from "react";
import { EmptyState, ErrorState, LoadingSpinner, StatisticCard } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { fetchHealth } from "../services/incidentService";
import { fetchMcpStatus } from "../services/systemService";
import type { HealthData, MCPStatusData } from "../types/api";

export function SettingsPage() {
  const { backendStatus } = useAppContext();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [mcp, setMcp] = useState<MCPStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (backendStatus !== "healthy") {
      setLoading(false);
      return;
    }

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [healthData, mcpData] = await Promise.all([fetchHealth(), fetchMcpStatus()]);
        setHealth(healthData);
        setMcp(mcpData);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load settings");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [backendStatus]);

  if (loading) {
    return <LoadingSpinner label="Loading system settings..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  }

  if (!health || !mcp) {
    return (
      <EmptyState
        title="Settings unavailable"
        description="Connect to the backend to view runtime and MCP configuration."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Settings</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Runtime health, ADK, and MCP tool registration status
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatisticCard title="Application" value={health.application_name} subtitle={health.version} />
        <StatisticCard
          title="AI Runtime"
          value={health.runtime ? "Ready" : "Unavailable"}
          subtitle={`${health.registered_agents ?? 0} agents registered`}
        />
        <StatisticCard
          title="MCP Tools"
          value={mcp.tool_count}
          subtitle={mcp.mcp ? "Server running" : "Server stopped"}
        />
        <StatisticCard
          title="Database"
          value={health.database_connected ? "Connected" : "Disconnected"}
          subtitle={`Uptime ${health.uptime_seconds.toFixed(0)}s`}
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100">Registered MCP tools</h3>
        <ul className="mt-3 space-y-1 text-sm text-slate-600 dark:text-slate-300">
          {mcp.tools.map((tool) => (
            <li key={tool}>{tool}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
