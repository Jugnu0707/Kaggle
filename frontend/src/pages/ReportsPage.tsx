import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { EmptyState, ErrorState, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { listIncidents } from "../services/incidentService";

interface ReportRow {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at: string;
}

export function ReportsPage() {
  const { backendStatus } = useAppContext();
  const [rows, setRows] = useState<ReportRow[]>([]);
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
        const incidents = await listIncidents({ page: 1, page_size: 50 });
        setRows(
          incidents.items.map((item) => ({
            id: item.id,
            title: item.title,
            severity: item.severity,
            status: item.status,
            created_at: item.created_at,
          })),
        );
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load reports");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [backendStatus]);

  if (loading) {
    return <LoadingSpinner label="Loading incident reports..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  }

  if (rows.length === 0) {
    return (
      <EmptyState
        title="No incident reports yet"
        description="Create an incident, run an investigation, and generate an executive report to see entries here."
      />
    );
  }

  const columns = [
    {
      key: "title",
      header: "Incident",
      render: (row: ReportRow) => (
        <Link
          to={`/incidents/${row.id}`}
          className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
        >
          {row.title}
        </Link>
      ),
    },
    { key: "severity", header: "Severity", render: (row: ReportRow) => row.severity },
    { key: "status", header: "Status", render: (row: ReportRow) => row.status },
    {
      key: "report",
      header: "Executive Report",
      render: (row: ReportRow) => (
        <Link
          to={`/incidents/${row.id}`}
          className="text-sm text-indigo-600 hover:underline dark:text-indigo-400"
        >
          View report tab
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Reports</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Executive and technical reports are available on each incident detail page.
        </p>
      </div>
      <DataTable columns={columns} data={rows} />
    </div>
  );
}
