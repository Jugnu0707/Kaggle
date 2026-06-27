import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, EmptyState, ErrorState, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { getIncident } from "../services/incidentService";
import {
  runInvestigation,
  type InvestigationPackage,
} from "../services/investigationService";
import type { IncidentDetail } from "../types/api";

const PIPELINE_STEPS = [
  "Evidence",
  "Threat Intelligence",
  "MITRE",
  "Risk",
  "Response",
  "Executive Report",
  "Guardian",
  "Timeline",
  "Evaluation",
];

function stepStatus(
  step: string,
  running: boolean,
  currentStep: string | null,
  result: InvestigationPackage | null,
): "pending" | "running" | "completed" | "failed" {
  if (!result) {
    if (running && currentStep === step) return "running";
    return "pending";
  }
  if (result.agents_completed.includes(step)) return "completed";
  if (result.agents_failed.includes(step)) return "failed";
  return "pending";
}

function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
      <div
        className="h-2 rounded-full bg-indigo-500 transition-all duration-500 dark:bg-indigo-400"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  );
}

function StageTimeline({
  steps,
  running,
  currentStep,
  result,
}: {
  steps: string[];
  running: boolean;
  currentStep: string | null;
  result: InvestigationPackage | null;
}) {
  return (
    <ol className="space-y-3">
      {steps.map((step) => {
        const status = stepStatus(step, running, currentStep, result);
        const stage = result?.stages.find((item) => item.agent === step);

        return (
          <li
            key={step}
            className="flex items-start gap-3 rounded-lg border border-slate-200 px-4 py-3 dark:border-slate-800"
          >
            <span
              className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                status === "completed"
                  ? "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300"
                  : status === "failed"
                    ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300"
                    : status === "running"
                      ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                      : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400"
              }`}
            >
              {status === "completed" ? "✓" : status === "failed" ? "!" : status === "running" ? "…" : "·"}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{step}</p>
                {stage && (
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {stage.duration_ms} ms
                  </span>
                )}
              </div>
              {stage?.fallback_used && (
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Fallback engine used</p>
              )}
              {stage?.error && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400">{stage.error}</p>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

export function InvestigationRunnerPage() {
  const { id } = useParams<{ id: string }>();
  const { backendStatus } = useAppContext();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [result, setResult] = useState<InvestigationPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || backendStatus !== "healthy") {
      setLoading(false);
      return;
    }

    const loadIncident = async () => {
      try {
        const data = await getIncident(id);
        setIncident(data);
      } catch {
        setIncident(null);
      } finally {
        setLoading(false);
      }
    };

    void loadIncident();
  }, [id, backendStatus]);

  const animateProgress = useCallback(() => {
    let stepIndex = 0;
    setProgress(5);
    setCurrentStep(PIPELINE_STEPS[0]);

    const interval = window.setInterval(() => {
      stepIndex += 1;
      if (stepIndex < PIPELINE_STEPS.length) {
        setCurrentStep(PIPELINE_STEPS[stepIndex]);
        setProgress(Math.min(90, ((stepIndex + 1) / PIPELINE_STEPS.length) * 90));
      }
    }, 900);

    return interval;
  }, []);

  const handleStartInvestigation = async () => {
    if (!id) return;

    setRunning(true);
    setError(null);
    setResult(null);
    const interval = animateProgress();

    try {
      const packageResult = await runInvestigation(id);
      setResult(packageResult);
      setProgress(100);
      setCurrentStep(null);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Investigation failed");
      setProgress(0);
      setCurrentStep(null);
    } finally {
      window.clearInterval(interval);
      setRunning(false);
    }
  };

  const completedCount = result?.agents_completed.length ?? 0;
  const failedCount = result?.agents_failed.length ?? 0;

  const statusLabel = useMemo(() => {
    if (running) return "Running";
    if (!result) return "Ready";
    return result.status.charAt(0).toUpperCase() + result.status.slice(1);
  }, [running, result]);

  if (loading) {
    return <LoadingSpinner label="Loading incident..." />;
  }

  if (!incident) {
    return (
      <EmptyState
        title="Incident not found"
        description="Select a valid incident to run an investigation."
        action={
          <Link
            to="/incidents"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
          >
            Back to incidents
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
            Investigation Runner
          </h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {incident.title} · End-to-end Coordinator workflow
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleStartInvestigation()}
          disabled={running || backendStatus !== "healthy"}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span>{running ? "Running Investigation…" : "▶ Start Investigation"}</span>
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500 dark:text-slate-400">Status</p>
          <p className="mt-2 text-xl font-semibold text-slate-900 dark:text-slate-100">
            {statusLabel}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500 dark:text-slate-400">Duration</p>
          <p className="mt-2 text-xl font-semibold text-slate-900 dark:text-slate-100">
            {result ? `${result.duration_ms} ms` : running ? "…" : "—"}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500 dark:text-slate-400">Completed Agents</p>
          <p className="mt-2 text-xl font-semibold text-green-600 dark:text-green-400">
            {running ? "…" : completedCount}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500 dark:text-slate-400">Failed Agents</p>
          <p className="mt-2 text-xl font-semibold text-red-600 dark:text-red-400">
            {running ? "…" : failedCount}
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
            Execution Progress
          </h3>
          {currentStep && (
            <span className="text-sm text-indigo-600 dark:text-indigo-400">
              Running: {currentStep}
            </span>
          )}
        </div>
        <ProgressBar progress={progress} />
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          {running
            ? "Coordinator is executing agents in sequence with Guardian validation."
            : result
              ? "Investigation workflow finished."
              : "Press Start Investigation to run the full pipeline."}
        </p>
      </section>

      {error && <ErrorState message={error} onRetry={() => void handleStartInvestigation()} />}

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
          Execution Timeline
        </h3>
        <div className="mt-4">
          <StageTimeline
            steps={PIPELINE_STEPS}
            running={running}
            currentStep={currentStep}
            result={result}
          />
        </div>
      </section>

      {result && (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
            Investigation Package
          </h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Overall Risk</p>
              <div className="mt-1">
                <Badge label={result.overall_risk} tone={result.overall_risk} />
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Evaluation Score</p>
              <p className="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">
                {result.evaluation_score ?? "—"}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Execution ID</p>
              <p className="mt-1 text-sm font-mono text-slate-700 dark:text-slate-300">
                {result.execution_id}
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <Link
              to={`/incidents/${id}`}
              className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
            >
              View incident details
            </Link>
            <Link
              to="/evaluation"
              className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
            >
              Open evaluation dashboard
            </Link>
          </div>
        </section>
      )}
    </div>
  );
}
