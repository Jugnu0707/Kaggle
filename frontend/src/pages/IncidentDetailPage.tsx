import { useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, ConfidenceBadge, EmptyState, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { isBackendUnavailableError } from "../services/apiClient";
import { getIncident } from "../services/incidentService";
import { getIncidentMitreMappings } from "../services/mitreService";
import type { IncidentDetail, MitreFinding } from "../types/api";
import { formatDate } from "../utils/format";

type IncidentTab = "overview" | "mitre";

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { backendStatus } = useAppContext();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [mitreFindings, setMitreFindings] = useState<MitreFinding[]>([]);
  const [activeTab, setActiveTab] = useState<IncidentTab>("overview");
  const [loading, setLoading] = useState(true);
  const [mitreLoading, setMitreLoading] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [backendUnavailable, setBackendUnavailable] = useState(false);
  const [mitreError, setMitreError] = useState<string | null>(null);

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

  useEffect(() => {
    if (!id || backendStatus !== "healthy" || activeTab !== "mitre") {
      return;
    }

    const loadMitre = async () => {
      setMitreLoading(true);
      setMitreError(null);
      try {
        const response = await getIncidentMitreMappings(id);
        setMitreFindings(response.items);
      } catch (loadError) {
        setMitreFindings([]);
        if (isBackendUnavailableError(loadError)) {
          setMitreError("MITRE mappings are unavailable while the backend is offline.");
        } else {
          setMitreError("Failed to load MITRE mappings.");
        }
      } finally {
        setMitreLoading(false);
      }
    };

    void loadMitre();
  }, [activeTab, backendStatus, id]);

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

      <div className="border-b border-slate-200 dark:border-slate-800">
        <nav className="-mb-px flex gap-6">
          <TabButton
            label="Overview"
            active={activeTab === "overview"}
            onClick={() => setActiveTab("overview")}
          />
          <TabButton
            label="MITRE ATT&CK"
            active={activeTab === "mitre"}
            onClick={() => setActiveTab("mitre")}
          />
        </nav>
      </div>

      {activeTab === "overview" ? (
        <OverviewTab incident={incident} />
      ) : (
        <MitreTab
          findings={mitreFindings}
          loading={mitreLoading}
          error={mitreError}
        />
      )}
    </div>
  );
}

function TabButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
        active
          ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
          : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
      }`}
    >
      {label}
    </button>
  );
}

function OverviewTab({ incident }: { incident: IncidentDetail }) {
  return (
    <>
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Overview</h3>
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          <DetailItem label="Created At" value={formatDate(incident.created_at)} />
          <DetailItem label="Updated At" value={formatDate(incident.updated_at)} />
          <DetailItem label="Confidence Score" value={incident.confidence_score.toFixed(2)} />
          <DetailItem
            label="Investigation Status"
            value={incident.investigation?.investigation_status ?? "Not started"}
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
              value={incident.investigation.duration_seconds?.toString() ?? "Not available"}
            />
            <DetailItem label="Status" value={incident.investigation.investigation_status} />
          </dl>
        </section>
      )}
    </>
  );
}

function MitreTab({
  findings,
  loading,
  error,
}: {
  findings: MitreFinding[];
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return <LoadingSpinner label="Loading MITRE mappings..." />;
  }

  if (error) {
    return <EmptyState title="MITRE mappings unavailable" description={error} />;
  }

  if (findings.length === 0) {
    return (
      <EmptyState
        title="No MITRE mappings found"
        description="Run the MITRE Mapping Agent on this incident to populate ATT&CK technique mappings."
      />
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">MITRE ATT&CK</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead>
            <tr className="text-left text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              <th className="px-3 py-2">Technique</th>
              <th className="px-3 py-2">Tactic</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-900">
            {findings.map((finding) => (
              <tr key={finding.id}>
                <td className="px-3 py-4 text-sm text-slate-900 dark:text-slate-100">
                  <div className="font-medium">{finding.technique_name}</div>
                  <div className="font-mono text-xs text-slate-500 dark:text-slate-400">
                    {finding.technique_id}
                  </div>
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  {finding.tactic}
                </td>
                <td className="px-3 py-4">
                  <ConfidenceBadge value={finding.confidence} />
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  <ul className="list-disc space-y-1 pl-4">
                    {finding.evidence.map((item) => (
                      <li key={item} className="font-mono text-xs">
                        {item}
                      </li>
                    ))}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
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
