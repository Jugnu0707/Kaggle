import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { Badge, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { listIncidents } from "../services/incidentService";
import type { Incident } from "../types/api";
import { formatDate, truncateId } from "../utils/format";

const EMPTY_INCIDENTS_MESSAGE =
  "No incidents found. Create an incident or upload a log.";

export function IncidentsPage() {
  const navigate = useNavigate();
  const { backendStatus } = useAppContext();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    if (backendStatus !== "healthy") {
      setIncidents([]);
      setTotalPages(1);
      setLoading(false);
      return;
    }

    const loadIncidents = async () => {
      setLoading(true);
      try {
        const data = await listIncidents({ page, page_size: 10 });
        setIncidents(data.items);
        setTotalPages(data.total_pages || 1);
      } catch {
        setIncidents([]);
        setTotalPages(1);
      } finally {
        setLoading(false);
      }
    };

    void loadIncidents();
  }, [backendStatus, page]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Incidents</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Browse and inspect security incidents
        </p>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
        {loading && backendStatus === "healthy" ? (
          <LoadingSpinner label="Loading incidents..." />
        ) : (
          <>
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
            <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 dark:border-slate-800">
              <button
                type="button"
                disabled={page <= 1 || backendStatus !== "healthy"}
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
                disabled={page >= totalPages || backendStatus !== "healthy"}
                onClick={() => setPage((current) => current + 1)}
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50 dark:border-slate-700"
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
