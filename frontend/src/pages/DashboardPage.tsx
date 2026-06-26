import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { Badge, ErrorState, LoadingSpinner, StatisticCard } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { fetchDashboardStats } from "../services/dashboardService";
import { listIncidents } from "../services/incidentService";
import { getErrorMessage } from "../services/apiClient";
import type { DashboardStats, Incident } from "../types/api";
import { formatDate, truncateId } from "../utils/format";

export function DashboardPage() {
  const navigate = useNavigate();
  const { backendStatus } = useAppContext();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, incidentData] = await Promise.all([
        fetchDashboardStats(),
        listIncidents({ page: 1, page_size: 5 }),
      ]);
      setStats(statsData);
      setIncidents(incidentData.items);
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (backendStatus !== "unavailable") {
      void loadDashboard();
    } else {
      setLoading(false);
      setError("Backend unavailable. Please check that the API server is running.");
    }
  }, [backendStatus]);

  if (loading) {
    return <LoadingSpinner label="Loading dashboard..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadDashboard()} />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Dashboard</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Overview of incidents and uploaded logs
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatisticCard title="Total Incidents" value={stats?.total_incidents ?? 0} />
        <StatisticCard title="Critical Incidents" value={stats?.critical_incidents ?? 0} />
        <StatisticCard title="High Incidents" value={stats?.high_incidents ?? 0} />
        <StatisticCard title="Uploaded Logs" value={stats?.uploaded_logs ?? 0} />
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="border-b border-slate-200 px-4 py-4 dark:border-slate-800">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
            Recent Incidents
          </h3>
        </div>
        <DataTable
          data={incidents}
          onRowClick={(incident) => navigate(`/incidents/${incident.id}`)}
          emptyMessage="No incidents recorded yet."
          columns={[
            {
              key: "id",
              header: "Incident ID",
              render: (row) => (
                <span className="font-mono text-xs">{truncateId(row.id, 12)}</span>
              ),
            },
            { key: "title", header: "Title", render: (row) => row.title },
            {
              key: "severity",
              header: "Severity",
              render: (row) => <Badge label={row.severity} />,
            },
            {
              key: "status",
              header: "Status",
              render: (row) => <Badge label={row.status} />,
            },
            { key: "source", header: "Source", render: (row) => row.source },
            {
              key: "created_at",
              header: "Created At",
              render: (row) => formatDate(row.created_at),
            },
          ]}
        />
      </section>
    </div>
  );
}
