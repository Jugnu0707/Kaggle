import { useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, EmptyState, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { isBackendUnavailableError } from "../services/apiClient";
import { getIncident } from "../services/incidentService";
import type { IncidentDetail } from "../types/api";
import { formatDate } from "../utils/format";

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { backendStatus } = useAppContext();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [backendUnavailable, setBackendUnavailable] = useState(false);

  useEffect(() => {
    if (!id) {
      setNotFound(true);
      setLoading(false);
      return;
    }

    if (backendStatus !== "healthy") {
      setIncident(null);
      setBackendUnavailable(true);
      setLoading(false);
      return;
    }

    const loadIncident = async () => {
      setLoading(true);
      setNotFound(false);
      setBackendUnavailable(false);
      try {
        setIncident(await getIncident(id));
      } catch (loadError) {
        setIncident(null);
        if (isBackendUnavailableError(loadError)) {
          setBackendUnavailable(true);
        } else {
          setNotFound(true);
        }
      } finally {
        setLoading(false);
      }
    };

    void loadIncident();
  }, [backendStatus, id]);

  if (loading) {
    return <LoadingSpinner label="Loading incident details..." />;
  }

  if (backendUnavailable) {
    return (
      <div className="space-y-4">
        <Link to="/incidents" className="text-sm text-indigo-600 hover:underline dark:text-indigo-400">
          Back to incidents
        </Link>
        <EmptyState
          title="Incident details unavailable"
          description="The backend is currently unavailable. Return to the incidents list and try again later."
        />
      </div>
    );
  }

  if (notFound || !incident) {
    return (
      <div className="space-y-4">
        <Link to="/incidents" className="text-sm text-indigo-600 hover:underline dark:text-indigo-400">
          Back to incidents
        </Link>
        <EmptyState
          title="Incident not found"
          description="This incident does not exist or may have been removed."
          action={
            <Link
              to="/incidents"
              className="inline-flex rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Back to incidents
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/incidents" className="text-sm text-indigo-600 hover:underline dark:text-indigo-400">
          Back to incidents
        </Link>
        <h2 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-100">
          {incident.title}
        </h2>
        <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">{incident.id}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <InfoCard label="Severity" value={<Badge label={incident.severity} />} />
        <InfoCard label="Status" value={<Badge label={incident.status} />} />
        <InfoCard label="Source" value={incident.source} />
        <InfoCard label="Evidence Count" value={String(incident.evidence_count)} />
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Overview</h3>
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          <DetailItem label="Created At" value={formatDate(incident.created_at)} />
          <DetailItem label="Updated At" value={formatDate(incident.updated_at)} />
          <DetailItem label="Confidence Score" value={incident.confidence_score.toFixed(2)} />
          <DetailItem
            label="Investigation Status"
            value={
              incident.investigation?.investigation_status ?? "Not started"
            }
          />
        </dl>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Description</h3>
        <p className="mt-3 text-sm leading-6 text-slate-700 dark:text-slate-300">
          {incident.description}
        </p>
      </section>

      {incident.investigation && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Investigation</h3>
          <dl className="mt-4 grid gap-4 sm:grid-cols-2">
            <DetailItem label="Started At" value={formatDate(incident.investigation.started_at)} />
            <DetailItem
              label="Completed At"
              value={
                incident.investigation.completed_at
                  ? formatDate(incident.investigation.completed_at)
                  : "In progress"
              }
            />
            <DetailItem
              label="Duration (seconds)"
              value={
                incident.investigation.duration_seconds?.toString() ?? "Not available"
              }
            />
            <DetailItem
              label="Status"
              value={incident.investigation.investigation_status}
            />
          </dl>
        </section>
      )}
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </p>
      <div className="mt-2 text-sm text-slate-900 dark:text-slate-100">{value}</div>
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-slate-900 dark:text-slate-100">{value}</dd>
    </div>
  );
}
