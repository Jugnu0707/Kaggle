import { useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { TimelineTab } from "../components/TimelineTab";
import { Badge, ConfidenceBadge, EmptyState, LoadingSpinner, ReputationBadge, SourceBadge, ValidationBadge } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { isBackendUnavailableError } from "../services/apiClient";
import { getIncidentGuardianAudits } from "../services/guardianService";
import { getIncidentExecutiveReport } from "../services/executiveReportService";
import { getIncident } from "../services/incidentService";
import { getIncidentMitreMappings } from "../services/mitreService";
import { getIncidentResponsePlan } from "../services/responseService";
import { getIncidentRiskAssessment } from "../services/riskService";
import { getIncidentThreatIntelligence } from "../services/threatIntelligenceService";
import { getIncidentTimeline } from "../services/timelineService";
import type { TimelineEvent } from "../services/timelineService";
import type {
  ExecutiveReportRecord,
  GuardianAuditRecord,
  IncidentDetail,
  MitreFinding,
  ResponsePlanRecord,
  RiskAssessmentRecord,
  ThreatIntelligenceFindingRecord,
} from "../types/api";
import { formatDate } from "../utils/format";

type IncidentTab =
  | "overview"
  | "timeline"
  | "threat-intelligence"
  | "mitre"
  | "risk"
  | "response"
  | "executive-report"
  | "guardian-audit";

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { backendStatus } = useAppContext();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [mitreFindings, setMitreFindings] = useState<MitreFinding[]>([]);
  const [threatFindings, setThreatFindings] = useState<ThreatIntelligenceFindingRecord[]>([]);
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessmentRecord | null>(null);
  const [responsePlan, setResponsePlan] = useState<ResponsePlanRecord | null>(null);
  const [executiveReport, setExecutiveReport] = useState<ExecutiveReportRecord | null>(null);
  const [guardianAudits, setGuardianAudits] = useState<GuardianAuditRecord[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [timelineSummary, setTimelineSummary] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<IncidentTab>("overview");
  const [loading, setLoading] = useState(true);
  const [mitreLoading, setMitreLoading] = useState(false);
  const [threatLoading, setThreatLoading] = useState(false);
  const [riskLoading, setRiskLoading] = useState(false);
  const [responseLoading, setResponseLoading] = useState(false);
  const [executiveLoading, setExecutiveLoading] = useState(false);
  const [guardianLoading, setGuardianLoading] = useState(false);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [backendUnavailable, setBackendUnavailable] = useState(false);
  const [mitreError, setMitreError] = useState<string | null>(null);
  const [threatError, setThreatError] = useState<string | null>(null);
  const [threatNotFound, setThreatNotFound] = useState(false);
  const [riskError, setRiskError] = useState<string | null>(null);
  const [riskNotFound, setRiskNotFound] = useState(false);
  const [responseError, setResponseError] = useState<string | null>(null);
  const [responseNotFound, setResponseNotFound] = useState(false);
  const [executiveError, setExecutiveError] = useState<string | null>(null);
  const [executiveNotFound, setExecutiveNotFound] = useState(false);
  const [guardianError, setGuardianError] = useState<string | null>(null);
  const [guardianNotFound, setGuardianNotFound] = useState(false);
  const [timelineError, setTimelineError] = useState<string | null>(null);

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
    if (!id || backendStatus !== "healthy" || activeTab !== "threat-intelligence") {
      return;
    }

    const loadThreatIntel = async () => {
      setThreatLoading(true);
      setThreatError(null);
      setThreatNotFound(false);
      try {
        const response = await getIncidentThreatIntelligence(id);
        setThreatFindings(response.items);
        if (response.total === 0) {
          setThreatNotFound(true);
        }
      } catch (loadError) {
        setThreatFindings([]);
        if (isBackendUnavailableError(loadError)) {
          setThreatError("Threat intelligence is unavailable while the backend is offline.");
        } else if (loadError instanceof Error && loadError.message.includes("not found")) {
          setThreatNotFound(true);
        } else {
          setThreatError("Failed to load threat intelligence findings.");
        }
      } finally {
        setThreatLoading(false);
      }
    };

    void loadThreatIntel();
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

  useEffect(() => {
    if (!id || backendStatus !== "healthy" || activeTab !== "executive-report") {
      return;
    }

    const loadExecutiveReport = async () => {
      setExecutiveLoading(true);
      setExecutiveError(null);
      setExecutiveNotFound(false);
      try {
        setExecutiveReport(await getIncidentExecutiveReport(id));
      } catch (loadError) {
        setExecutiveReport(null);
        if (isBackendUnavailableError(loadError)) {
          setExecutiveError("Executive report is unavailable while the backend is offline.");
        } else if (loadError instanceof Error && loadError.message.includes("not found")) {
          setExecutiveNotFound(true);
        } else {
          setExecutiveError("Failed to load executive report.");
        }
      } finally {
        setExecutiveLoading(false);
      }
    };

    void loadExecutiveReport();
  }, [activeTab, backendStatus, id]);

  useEffect(() => {
    if (!id || backendStatus !== "healthy" || activeTab !== "guardian-audit") {
      return;
    }

    const loadGuardianAudits = async () => {
      setGuardianLoading(true);
      setGuardianError(null);
      setGuardianNotFound(false);
      try {
        const response = await getIncidentGuardianAudits(id);
        setGuardianAudits(response.items);
        if (response.total === 0) {
          setGuardianNotFound(true);
        }
      } catch (loadError) {
        setGuardianAudits([]);
        if (isBackendUnavailableError(loadError)) {
          setGuardianError("Guardian audit records are unavailable while the backend is offline.");
        } else {
          setGuardianError("Failed to load Guardian audit records.");
        }
      } finally {
        setGuardianLoading(false);
      }
    };

    void loadGuardianAudits();
  }, [activeTab, backendStatus, id]);

  useEffect(() => {
    if (!id || backendStatus !== "healthy" || activeTab !== "timeline") {
      return;
    }

    const loadTimeline = async () => {
      setTimelineLoading(true);
      setTimelineError(null);
      try {
        const response = await getIncidentTimeline(id);
        setTimelineEvents(response.timeline);
        setTimelineSummary(response.investigation_summary);
      } catch (loadError) {
        setTimelineEvents([]);
        setTimelineSummary(null);
        if (isBackendUnavailableError(loadError)) {
          setTimelineError("Timeline is unavailable while the backend is offline.");
        } else {
          setTimelineError("Failed to load investigation timeline.");
        }
      } finally {
        setTimelineLoading(false);
      }
    };

    void loadTimeline();
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
            label="Timeline"
            active={activeTab === "timeline"}
            onClick={() => setActiveTab("timeline")}
          />
          <TabButton
            label="Threat Intelligence"
            active={activeTab === "threat-intelligence"}
            onClick={() => setActiveTab("threat-intelligence")}
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
          <TabButton
            label="Executive Report"
            active={activeTab === "executive-report"}
            onClick={() => setActiveTab("executive-report")}
          />
          <TabButton
            label="Guardian Audit"
            active={activeTab === "guardian-audit"}
            onClick={() => setActiveTab("guardian-audit")}
          />
        </nav>
      </div>

      {activeTab === "overview" ? (
        <OverviewTab incident={incident} />
      ) : activeTab === "timeline" ? (
        <TimelineTab
          incidentId={incident.id}
          timeline={timelineEvents}
          summary={timelineSummary}
          loading={timelineLoading}
          error={timelineError}
        />
      ) : activeTab === "threat-intelligence" ? (
        <ThreatIntelligenceTab
          findings={threatFindings}
          loading={threatLoading}
          error={threatError}
          notFound={threatNotFound}
        />
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
      ) : activeTab === "response" ? (
        <ResponseTab
          plan={responsePlan}
          loading={responseLoading}
          error={responseError}
          notFound={responseNotFound}
        />
      ) : activeTab === "executive-report" ? (
        <ExecutiveReportTab
          report={executiveReport}
          loading={executiveLoading}
          error={executiveError}
          notFound={executiveNotFound}
        />
      ) : (
        <GuardianAuditTab
          audits={guardianAudits}
          loading={guardianLoading}
          error={guardianError}
          notFound={guardianNotFound}
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

function ThreatIntelligenceTab({
  findings,
  loading,
  error,
  notFound,
}: {
  findings: ThreatIntelligenceFindingRecord[];
  loading: boolean;
  error: string | null;
  notFound: boolean;
}) {
  if (loading) {
    return <LoadingSpinner label="Loading threat intelligence..." />;
  }

  if (error) {
    return <EmptyState title="Threat intelligence unavailable" description={error} />;
  }

  if (notFound || findings.length === 0) {
    return (
      <EmptyState
        title="No threat intelligence findings"
        description="Run the Threat Intelligence Agent on this incident to enrich extracted IOCs."
      />
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Threat Intelligence</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead>
            <tr className="text-left text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              <th className="px-3 py-2">Indicator</th>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Reputation</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-900">
            {findings.map((finding) => (
              <tr key={finding.id}>
                <td className="px-3 py-4 font-mono text-xs text-slate-900 dark:text-slate-100">
                  {finding.indicator}
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  {finding.indicator_type}
                </td>
                <td className="px-3 py-4">
                  <ReputationBadge reputation={finding.reputation} />
                </td>
                <td className="px-3 py-4">
                  <ConfidenceBadge value={finding.confidence} />
                </td>
                <td className="px-3 py-4">
                  <SourceBadge source={finding.source} />
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  <p>{finding.description}</p>
                  <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                    {finding.analyst_notes}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
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

function GuardianAuditTab({
  audits,
  loading,
  error,
  notFound,
}: {
  audits: GuardianAuditRecord[];
  loading: boolean;
  error: string | null;
  notFound: boolean;
}) {
  if (loading) {
    return <LoadingSpinner label="Loading Guardian audit records..." />;
  }

  if (error) {
    return <EmptyState title="Guardian audit unavailable" description={error} />;
  }

  if (notFound || audits.length === 0) {
    return (
      <EmptyState
        title="No Guardian audit records"
        description="Run the agent pipeline on this incident to populate Guardian validation audits."
      />
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Guardian Audit</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead>
            <tr className="text-left text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              <th className="px-3 py-2">Agent</th>
              <th className="px-3 py-2">Validation Status</th>
              <th className="px-3 py-2">Issues Found</th>
              <th className="px-3 py-2">Action Taken</th>
              <th className="px-3 py-2">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-900">
            {audits.map((audit) => (
              <tr key={audit.id}>
                <td className="px-3 py-4 text-sm text-slate-900 dark:text-slate-100">
                  {audit.agent_name}
                </td>
                <td className="px-3 py-4">
                  <ValidationBadge status={audit.validation_status} />
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  {audit.issues_found.length > 0 ? (
                    <ul className="list-disc space-y-1 pl-4">
                      {audit.issues_found.map((issue) => (
                        <li key={issue}>{issue}</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-slate-500 dark:text-slate-400">None</span>
                  )}
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  {audit.action_taken}
                </td>
                <td className="px-3 py-4 text-sm text-slate-700 dark:text-slate-300">
                  {formatDate(audit.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ExecutiveReportTab({
  report,
  loading,
  error,
  notFound,
}: {
  report: ExecutiveReportRecord | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}) {
  const [copyStatus, setCopyStatus] = useState<string | null>(null);

  if (loading) {
    return <LoadingSpinner label="Loading executive report..." />;
  }

  if (error) {
    return <EmptyState title="Executive report unavailable" description={error} />;
  }

  if (notFound || !report) {
    return (
      <EmptyState
        title="No executive report found"
        description="Run the Executive Report Agent on this incident to generate a leadership-ready report."
      />
    );
  }

  const handleCopyMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(report.markdown_report);
      setCopyStatus("Copied to clipboard");
      window.setTimeout(() => setCopyStatus(null), 2000);
    } catch {
      setCopyStatus("Unable to copy markdown");
    }
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([report.markdown_report], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `executive-report-${report.incident_id}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="space-y-6">
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-100">
        This report omits sensitive technical details.
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
              {report.title}
            </h3>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Generated {formatDate(report.created_at)}
            </p>
          </div>
          <SourceBadge source={report.source} />
        </div>

        <div className="mt-6 space-y-6">
          <div>
            <h4 className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Summary
            </h4>
            <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
              {report.executive_summary}
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Business Impact
            </h4>
            <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
              {report.business_impact}
            </p>
          </div>

          <ActionList title="Findings" actions={report.key_findings} />
          <ActionList title="Recommendations" actions={report.recommended_actions} />
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
            Markdown Preview
          </h3>
          <div className="flex flex-wrap items-center gap-2">
            {copyStatus && (
              <span className="text-xs text-emerald-600 dark:text-emerald-400">{copyStatus}</span>
            )}
            <button
              type="button"
              onClick={() => void handleCopyMarkdown()}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900"
            >
              Copy Markdown
            </button>
            <button
              type="button"
              onClick={handleDownloadMarkdown}
              className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Download Markdown
            </button>
          </div>
        </div>
        <pre className="mt-4 max-h-[32rem] overflow-auto rounded-lg bg-slate-950 p-4 text-xs leading-6 text-slate-100">
          {report.markdown_report}
        </pre>
      </section>
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
