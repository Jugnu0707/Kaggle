import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { Badge, ErrorState, LoadingSpinner } from "../components/ui";
import { listIncidents } from "../services/incidentService";
import { getErrorMessage } from "../services/apiClient";
import type { Incident } from "../types/api";
import { formatDate, truncateId } from "../utils/format";

export function IncidentsPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadIncidents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listIncidents({ page, page_size: 10 });
      setIncidents(data.items);
      setTotalPages(data.total_pages || 1);
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadIncidents();
  }, [page]);

  if (loading) {
    return <LoadingSpinner label="Loading incidents..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadIncidents()} />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Incidents</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Browse and inspect security incidents
        </p>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <DataTable
          data={incidents}
          onRowClick={(incident) => navigate(`/incidents/${incident.id}`)}
          emptyMessage="No incidents found."
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
        <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 dark:border-slate-800">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((current) => current - 1)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50 dark:border-slate-700"
          >
            Previous
          </button>
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50 dark:border-slate-700"
          >
            Next
          </button>
        </div>
      </section>
    </div>
  );
}
