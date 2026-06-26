import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { Badge, LoadingSpinner, StatisticCard } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { fetchDashboardStats } from "../services/dashboardService";
import { listIncidents } from "../services/incidentService";
import type { DashboardStats, Incident } from "../types/api";
import { formatDate, truncateId } from "../utils/format";

const EMPTY_INCIDENTS_MESSAGE =
  "No incidents found. Create an incident or upload a log.";

const defaultStats: DashboardStats = {
  total_incidents: 0,
  critical_incidents: 0,
  high_incidents: 0,
  uploaded_logs: 0,
};

export function DashboardPage() {
  const navigate = useNavigate();
  const { backendStatus } = useAppContext();
  const [stats, setStats] = useState<DashboardStats>(defaultStats);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (backendStatus !== "healthy") {
      setStats(defaultStats);
      setIncidents([]);
      setLoading(false);
      return;
    }

    const loadDashboard = async () => {
      setLoading(true);
      try {
        const [statsData, incidentData] = await Promise.all([
          fetchDashboardStats(),
          listIncidents({ page: 1, page_size: 5 }),
        ]);
        setStats(statsData);
        setIncidents(incidentData.items);
      } catch {
        setStats(defaultStats);
        setIncidents([]);
      } finally {
        setLoading(false);
      }
    };

    void loadDashboard();
  }, [backendStatus]);

  if (loading && backendStatus === "healthy") {
    return <LoadingSpinner label="Loading dashboard..." />;
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
        <StatisticCard title="Total Incidents" value={stats.total_incidents} />
        <StatisticCard title="Critical Incidents" value={stats.critical_incidents} />
        <StatisticCard title="High Incidents" value={stats.high_incidents} />
        <StatisticCard title="Uploaded Logs" value={stats.uploaded_logs} />
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
          emptyMessage={EMPTY_INCIDENTS_MESSAGE}
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
        {incidents.length === 0 && backendStatus === "healthy" && (
          <div className="flex justify-center gap-3 border-t border-slate-200 px-4 py-4 dark:border-slate-800">
            <Link
              to="/incidents"
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900"
            >
              View incidents
            </Link>
            <Link
              to="/logs"
              className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Upload a log
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}
