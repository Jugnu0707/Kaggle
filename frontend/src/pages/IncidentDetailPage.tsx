import { useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, ConfidenceBadge, EmptyState, LoadingSpinner, SourceBadge } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { isBackendUnavailableError } from "../services/apiClient";
import { getIncident } from "../services/incidentService";
import { getIncidentMitreMappings } from "../services/mitreService";
import { getIncidentResponsePlan } from "../services/responseService";
import { getIncidentRiskAssessment } from "../services/riskService";
import type { IncidentDetail, MitreFinding, ResponsePlanRecord, RiskAssessmentRecord } from "../types/api";
import { formatDate } from "../utils/format";

type IncidentTab = "overview" | "mitre" | "risk" | "response";

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { backendStatus } = useAppContext();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [mitreFindings, setMitreFindings] = useState<MitreFinding[]>([]);
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessmentRecord | null>(null);
  const [responsePlan, setResponsePlan] = useState<ResponsePlanRecord | null>(null);
  const [activeTab, setActiveTab] = useState<IncidentTab>("overview");
  const [loading, setLoading] = useState(true);
  const [mitreLoading, setMitreLoading] = useState(false);
  const [riskLoading, setRiskLoading] = useState(false);
  const [responseLoading, setResponseLoading] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [backendUnavailable, setBackendUnavailable] = useState(false);
  const [mitreError, setMitreError] = useState<string | null>(null);
  const [riskError, setRiskError] = useState<string | null>(null);
  const [riskNotFound, setRiskNotFound] = useState(false);
  const [responseError, setResponseError] = useState<string | null>(null);
  const [responseNotFound, setResponseNotFound] = useState(false);

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

  useEffect(() => {
    if (!id || backendStatus !== "healthy" || activeTab !== "risk") {
      return;
    }

    const loadRisk = async () => {
      setRiskLoading(true);
      setRiskError(null);
      setRiskNotFound(false);
      try {
        setRiskAssessment(await getIncidentRiskAssessment(id));
      } catch (loadError) {
        setRiskAssessment(null);
        if (isBackendUnavailableError(loadError)) {
          setRiskError("Risk assessment is unavailable while the backend is offline.");
        } else if (loadError instanceof Error && loadError.message.includes("not found")) {
          setRiskNotFound(true);
        } else {
          setRiskError("Failed to load risk assessment.");
        }
      } finally {
        setRiskLoading(false);
      }
    };

    void loadRisk();
  }, [activeTab, backendStatus, id]);

  useEffect(() => {
    if (!id || backendStatus !== "healthy" || activeTab !== "response") {
      return;
    }

    const loadResponse = async () => {
      setResponseLoading(true);
      setResponseError(null);
      setResponseNotFound(false);
      try {
        setResponsePlan(await getIncidentResponsePlan(id));
      } catch (loadError) {
        setResponsePlan(null);
        if (isBackendUnavailableError(loadError)) {
          setResponseError("Response plan is unavailable while the backend is offline.");
        } else if (loadError instanceof Error && loadError.message.includes("not found")) {
          setResponseNotFound(true);
        } else {
          setResponseError("Failed to load response plan.");
        }
      } finally {
        setResponseLoading(false);
      }
    };

    void loadResponse();
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
          <TabButton
            label="Risk Assessment"
            active={activeTab === "risk"}
            onClick={() => setActiveTab("risk")}
          />
          <TabButton
            label="Response Plan"
            active={activeTab === "response"}
            onClick={() => setActiveTab("response")}
          />
        </nav>
      </div>

      {activeTab === "overview" ? (
        <OverviewTab incident={incident} />
      ) : activeTab === "mitre" ? (
        <MitreTab
          findings={mitreFindings}
          loading={mitreLoading}
          error={mitreError}
        />
      ) : activeTab === "risk" ? (
        <RiskTab
          assessment={riskAssessment}
          loading={riskLoading}
          error={riskError}
          notFound={riskNotFound}
        />
      ) : (
        <ResponseTab
          plan={responsePlan}
          loading={responseLoading}
          error={responseError}
          notFound={responseNotFound}
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

function RiskTab({
  assessment,
  loading,
  error,
  notFound,
}: {
  assessment: RiskAssessmentRecord | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}) {
  if (loading) {
    return <LoadingSpinner label="Loading risk assessment..." />;
  }

  if (error) {
    return <EmptyState title="Risk assessment unavailable" description={error} />;
  }

  if (notFound || !assessment) {
    return (
      <EmptyState
        title="No risk assessment found"
        description="Run the Risk Assessment Agent on this incident to generate an enterprise risk assessment."
      />
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Risk Assessment</h3>
        <SourceBadge source={assessment.source} />
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <InfoCard label="Risk Level" value={<Badge label={assessment.overall_risk} />} />
        <InfoCard label="Risk Score" value={String(assessment.risk_score)} />
        <InfoCard label="Priority" value={assessment.priority} />
        <InfoCard label="Confidence" value={<ConfidenceBadge value={assessment.confidence} />} />
      </div>

      <dl className="mt-6 grid gap-4 sm:grid-cols-2">
        <DetailItem label="Likelihood" value={assessment.likelihood} />
        <DetailItem label="Business Impact" value={assessment.business_impact} />
        <DetailItem label="Assessment Source" value={assessment.source} />
        <DetailItem label="Assessed At" value={formatDate(assessment.created_at)} />
      </dl>

      <div className="mt-6 space-y-4">
        <div>
          <h4 className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Summary
          </h4>
          <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
            {assessment.summary}
          </p>
        </div>
        <div>
          <h4 className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Reasoning
          </h4>
          <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
            {assessment.reasoning}
          </p>
        </div>
      </div>
    </section>
  );
}

function ResponseTab({
  plan,
  loading,
  error,
  notFound,
}: {
  plan: ResponsePlanRecord | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}) {
  if (loading) {
    return <LoadingSpinner label="Loading response plan..." />;
  }

  if (error) {
    return <EmptyState title="Response plan unavailable" description={error} />;
  }

  if (notFound || !plan) {
    return (
      <EmptyState
        title="No response plan found"
        description="Run the Response Planning Agent on this incident to generate an incident response plan."
      />
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Response Plan</h3>
        <SourceBadge source={plan.source} />
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <InfoCard label="Priority" value={plan.priority} />
        <InfoCard label="Assessment Source" value={plan.source} />
        <InfoCard label="Generated At" value={formatDate(plan.created_at)} />
      </div>

      <div className="mt-6 space-y-6">
        <ActionList title="Containment" actions={plan.containment} />
        <ActionList title="Eradication" actions={plan.eradication} />
        <ActionList title="Recovery" actions={plan.recovery} />
        <ActionList title="Monitoring" actions={plan.monitoring} />
      </div>

      <div className="mt-6">
        <h4 className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Executive Summary
        </h4>
        <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
          {plan.executive_summary}
        </p>
      </div>
    </section>
  );
}

function ActionList({ title, actions }: { title: string; actions: string[] }) {
  return (
    <div>
      <h4 className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {title}
      </h4>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-slate-700 dark:text-slate-300">
        {actions.map((action) => (
          <li key={action}>{action}</li>
        ))}
      </ul>
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
