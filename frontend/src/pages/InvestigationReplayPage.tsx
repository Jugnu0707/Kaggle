import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Badge, ConfidenceBadge, EmptyState, ErrorState, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import {
  exportInvestigationReplay,
  getInvestigationExplain,
  getInvestigationReplay,
  type InvestigationExplain,
  type InvestigationReplay,
  type InvestigationReplayStep,
} from "../services/investigationReplayService";

type StepVisualStatus = "completed" | "running" | "skipped" | "failed";

function stepVisualStatus(step: InvestigationReplayStep, activeStep: number): StepVisualStatus {
  if (step.step === activeStep) return "running";
  if (step.status === "skipped") return "skipped";
  if (step.status === "failed") return "failed";
  return "completed";
}

function statusRingClass(status: StepVisualStatus): string {
  switch (status) {
    case "completed":
      return "border-green-500 bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300";
    case "running":
      return "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300";
    case "skipped":
      return "border-slate-400 bg-slate-100 text-slate-600 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300";
    case "failed":
      return "border-red-500 bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300";
  }
}

function SourcePill({ source, fallbackUsed }: { source: string; fallbackUsed: boolean }) {
  if (fallbackUsed || source === "FALLBACK") {
    return (
      <span className="rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-800 dark:bg-orange-950 dark:text-orange-200">
        Fallback
      </span>
    );
  }
  if (source === "AI") {
    return (
      <span className="rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800 dark:bg-purple-950 dark:text-purple-200">
        AI
      </span>
    );
  }
  return (
    <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
      System
    </span>
  );
}

function AgentCard({
  step,
  active,
  expanded,
  onSelect,
  onToggle,
}: {
  step: InvestigationReplayStep;
  active: boolean;
  expanded: boolean;
  onSelect: () => void;
  onToggle: () => void;
}) {
  const visual = stepVisualStatus(step, active ? step.step : -1);

  return (
    <article
      className={`rounded-xl border p-4 transition ${
        active
          ? "border-blue-400 bg-blue-50/50 dark:border-blue-600 dark:bg-blue-950/30"
          : "border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950"
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <button type="button" onClick={onSelect} className="text-left">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Step {step.step}
          </p>
          <h3 className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-100">
            {step.agent}
          </h3>
        </button>
        <div className="flex flex-wrap items-center gap-2">
          <SourcePill source={step.source} fallbackUsed={step.fallback_used} />
          {step.confidence !== null && <ConfidenceBadge value={step.confidence} />}
          <span className="text-xs text-slate-500 dark:text-slate-400">{step.duration_ms} ms</span>
        </div>
      </div>

      <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{step.summary}</p>

      {step.explainability && (
        <button
          type="button"
          onClick={onToggle}
          className="mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
        >
          {expanded ? "Hide reasoning" : "Show reasoning"}
        </button>
      )}

      {expanded && step.explainability && (
        <div className="mt-3 space-y-2 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-800 dark:bg-slate-900">
          <p><span className="font-medium">Decision:</span> {step.explainability.decision}</p>
          <p><span className="font-medium">Reason:</span> {step.explainability.reason}</p>
          {step.explainability.evidence_used.length > 0 && (
            <div>
              <p className="font-medium">Evidence used</p>
              <ul className="mt-1 list-disc pl-5 text-slate-600 dark:text-slate-300">
                {step.explainability.evidence_used.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </article>
  );
}

export function InvestigationReplayPage() {
  const { runId } = useParams<{ runId: string }>();
  const { backendStatus } = useAppContext();
  const [replay, setReplay] = useState<InvestigationReplay | null>(null);
  const [explain, setExplain] = useState<InvestigationExplain | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(1);
  const [expandedStep, setExpandedStep] = useState<number | null>(null);
  const [autoPlay, setAutoPlay] = useState(false);
  const timerRef = useRef<number | null>(null);

  const loadReplay = useCallback(async () => {
    if (!runId) return;
    setLoading(true);
    setError(null);
    try {
      const [replayData, explainData] = await Promise.all([
        getInvestigationReplay(runId),
        getInvestigationExplain(runId),
      ]);
      setReplay(replayData);
      setExplain(explainData);
      setActiveStep(replayData.steps[0]?.step ?? 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load replay");
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    if (backendStatus !== "healthy") {
      setLoading(false);
      return;
    }
    void loadReplay();
  }, [backendStatus, loadReplay]);

  useEffect(() => {
    if (!autoPlay || !replay) return;

    timerRef.current = window.setInterval(() => {
      setActiveStep((current) => {
        const maxStep = replay.steps[replay.steps.length - 1]?.step ?? current;
        if (current >= maxStep) {
          setAutoPlay(false);
          return current;
        }
        return current + 1;
      });
    }, 1500);

    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current);
      }
    };
  }, [autoPlay, replay]);

  const activeStepData = useMemo(
    () => replay?.steps.find((step) => step.step === activeStep) ?? null,
    [replay, activeStep],
  );

  const handleExport = async (format: "json" | "markdown") => {
    if (!runId) return;
    const exported = await exportInvestigationReplay(runId, format);
    const blob = new Blob([exported.content], {
      type: format === "json" ? "application/json" : "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `investigation-replay-${runId}.${format === "json" ? "json" : "md"}`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  if (!runId) {
    return <EmptyState title="Missing run ID" description="Open replay from an investigation run." />;
  }

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <LoadingSpinner label="Loading investigation replay…" />
      </div>
    );
  }

  if (error || !replay || !explain) {
    return (
      <ErrorState
        message={error ?? "Replay data unavailable"}
        onRetry={() => void loadReplay()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
            Investigation Replay
          </h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Run {runId.slice(0, 8)}… · {replay.duration_ms} ms total
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setAutoPlay(true)}
            disabled={autoPlay}
            className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
          >
            Auto Play
          </button>
          <button
            type="button"
            onClick={() => setAutoPlay(false)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 dark:border-slate-700 dark:text-slate-200"
          >
            Pause
          </button>
          <button
            type="button"
            onClick={() => void handleExport("json")}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 dark:border-slate-700 dark:text-slate-200"
          >
            Export JSON
          </button>
          <button
            type="button"
            onClick={() => void handleExport("markdown")}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 dark:border-slate-700 dark:text-slate-200"
          >
            Export Markdown
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500">Overall Risk</p>
          <div className="mt-2"><Badge label={explain.overall_risk} tone={explain.overall_risk} /></div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500">AI Steps</p>
          <p className="mt-2 text-xl font-semibold text-purple-600">{explain.ai_usage_count}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500">Fallback Steps</p>
          <p className="mt-2 text-xl font-semibold text-orange-600">{explain.fallback_usage_count}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm text-slate-500">Evaluation Score</p>
          <p className="mt-2 text-xl font-semibold text-slate-900 dark:text-slate-100">
            {explain.evaluation_score ?? "—"}
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Summary</h3>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          {explain.overall_investigation_summary}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {replay.steps.map((step) => (
            <button
              key={step.step}
              type="button"
              onClick={() => {
                setActiveStep(step.step);
                setAutoPlay(false);
              }}
              className={`rounded-full border px-3 py-1 text-xs font-medium ${statusRingClass(
                stepVisualStatus(step, activeStep),
              )}`}
            >
              {step.step}. {step.agent}
            </button>
          ))}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="space-y-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Timeline</h3>
          <ol className="space-y-2">
            {replay.steps.map((step) => {
              const visual = stepVisualStatus(step, activeStep);
              return (
                <li key={step.step}>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveStep(step.step);
                      setAutoPlay(false);
                    }}
                    className={`flex w-full items-center gap-3 rounded-lg border px-3 py-2 text-left text-sm ${
                      step.step === activeStep
                        ? "border-blue-400 bg-blue-50 dark:border-blue-700 dark:bg-blue-950/40"
                        : "border-slate-200 dark:border-slate-800"
                    }`}
                  >
                    <span
                      className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-semibold ${statusRingClass(
                        visual,
                      )}`}
                    >
                      {step.step}
                    </span>
                    <span className="truncate text-slate-700 dark:text-slate-200">{step.agent}</span>
                  </button>
                </li>
              );
            })}
          </ol>
        </aside>

        <div className="space-y-4">
          {activeStepData && (
            <AgentCard
              step={activeStepData}
              active
              expanded={expandedStep === activeStepData.step}
              onSelect={() => setActiveStep(activeStepData.step)}
              onToggle={() =>
                setExpandedStep((current) =>
                  current === activeStepData.step ? null : activeStepData.step,
                )
              }
            />
          )}
          <Link
            to={`/incidents/${replay.incident_id}/investigate`}
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
          >
            Back to investigation runner
          </Link>
        </div>
      </div>
    </div>
  );
}
