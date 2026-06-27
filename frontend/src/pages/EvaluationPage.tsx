import { useEffect, useMemo, useState } from "react";
import { DataTable } from "../components/DataTable";
import { EmptyState, ErrorState, LoadingSpinner, StatisticCard } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { fetchEvaluationOverview } from "../services/evaluationService";
import type { AgentEvaluationSummary, EvaluationOverview } from "../types/api";

function scoreColor(score: number): string {
  if (score >= 90) return "text-green-600 dark:text-green-400";
  if (score >= 75) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

function BarChart({
  items,
  maxValue,
  valueKey,
  labelKey,
}: {
  items: AgentEvaluationSummary[];
  maxValue: number;
  valueKey: keyof AgentEvaluationSummary;
  labelKey: keyof AgentEvaluationSummary;
}) {
  const safeMax = maxValue > 0 ? maxValue : 1;

  return (
    <div className="space-y-3">
      {items.map((item) => {
        const value = Number(item[valueKey]);
        const width = Math.max(4, (value / safeMax) * 100);
        return (
          <div key={String(item[labelKey])}>
            <div className="mb-1 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span className="truncate pr-2">{String(item[labelKey])}</span>
              <span>{value.toFixed(0)}</span>
            </div>
            <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className="h-2 rounded-full bg-indigo-500 dark:bg-indigo-400"
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function UsageChart({ agents }: { agents: AgentEvaluationSummary[] }) {
  const maxUsage = Math.max(
    1,
    ...agents.map((agent) => agent.ai_used_count + agent.fallback_used_count),
  );

  return (
    <div className="space-y-3">
      {agents.map((agent) => {
        const total = agent.ai_used_count + agent.fallback_used_count;
        const aiWidth = (agent.ai_used_count / maxUsage) * 100;
        const fallbackWidth = (agent.fallback_used_count / maxUsage) * 100;
        return (
          <div key={agent.agent_name}>
            <div className="mb-1 text-xs text-slate-500 dark:text-slate-400">{agent.agent_name}</div>
            <div className="flex h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className="bg-indigo-500 dark:bg-indigo-400"
                style={{ width: `${aiWidth}%` }}
                title={`AI: ${agent.ai_used_count}`}
              />
              <div
                className="bg-slate-400 dark:bg-slate-500"
                style={{ width: `${fallbackWidth}%` }}
                title={`Fallback: ${agent.fallback_used_count}`}
              />
            </div>
            <div className="mt-1 flex gap-3 text-xs text-slate-500 dark:text-slate-400">
              <span>AI: {agent.ai_used_count}</span>
              <span>Fallback: {agent.fallback_used_count}</span>
              <span>Total: {total}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function EvaluationPage() {
  const { backendStatus } = useAppContext();
  const [overview, setOverview] = useState<EvaluationOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEvaluationOverview();
      setOverview(data);
    } catch (loadError) {
      setOverview(null);
      setError(loadError instanceof Error ? loadError.message : "Failed to load evaluation data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (backendStatus !== "healthy") {
      setOverview(null);
      setLoading(false);
      return;
    }
    void loadEvaluation();
  }, [backendStatus]);

  const maxLatency = useMemo(
    () => Math.max(0, ...((overview?.agents ?? []).map((agent) => agent.mean_execution_time_ms))),
    [overview],
  );

  const tableColumns = [
    {
      key: "agent_name",
      header: "Agent",
      render: (row: AgentEvaluationSummary) => row.agent_name,
    },
    {
      key: "health_score",
      header: "Health",
      render: (row: AgentEvaluationSummary) => (
        <span className={scoreColor(row.health_score)}>{row.health_score}</span>
      ),
    },
    {
      key: "success_rate",
      header: "Success Rate",
      render: (row: AgentEvaluationSummary) => `${row.success_rate.toFixed(1)}%`,
    },
    {
      key: "mean_execution_time_ms",
      header: "Latency (ms)",
      render: (row: AgentEvaluationSummary) => row.mean_execution_time_ms.toFixed(0),
    },
    {
      key: "accuracy",
      header: "Accuracy",
      render: (row: AgentEvaluationSummary) => row.accuracy,
    },
    {
      key: "ai_used_count",
      header: "AI Used",
      render: (row: AgentEvaluationSummary) => row.ai_used_count,
    },
    {
      key: "fallback_used_count",
      header: "Fallback",
      render: (row: AgentEvaluationSummary) => row.fallback_used_count,
    },
  ];

  if (loading && backendStatus === "healthy") {
    return <LoadingSpinner label="Running evaluation benchmarks..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadEvaluation()} />;
  }

  if (!overview) {
    return (
      <EmptyState
        title="No evaluation results"
        description="Connect to the backend to generate agent evaluation metrics."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
          Evaluation Dashboard
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Agent quality, reliability, and performance metrics
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatisticCard
          title="Overall Health Score"
          value={overview.overall_score}
          subtitle="Weighted agent health average"
        />
        <StatisticCard
          title="Success Rate"
          value={`${overview.overall_success_rate.toFixed(1)}%`}
          subtitle="Across all benchmark runs"
        />
        <StatisticCard
          title="Total Executions"
          value={overview.total_executions}
          subtitle="Benchmark executions recorded"
        />
        <StatisticCard
          title="Agents Benchmarked"
          value={overview.agents.length}
          subtitle="Coordinator through Timeline Engine"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatisticCard
          title="MCP Tool Executions"
          value={overview.tool_execution_count}
          subtitle={`${overview.tool_failure_count} failures recorded`}
        />
        <StatisticCard
          title="Mean ADK Session"
          value={`${overview.mean_adk_session_duration_ms.toFixed(1)} ms`}
          subtitle="Coordinator and agent session duration"
        />
        <StatisticCard
          title="Mean MCP Latency"
          value={`${overview.mean_mcp_latency_ms.toFixed(1)} ms`}
          subtitle="Per tool invocation"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatisticCard
          title="Investigation Duration"
          value={`${overview.mean_investigation_duration_ms.toFixed(0)} ms`}
          subtitle="Mean end-to-end investigation time"
        />
        <StatisticCard
          title="Agent Execution Time"
          value={`${overview.mean_agent_execution_time_ms.toFixed(1)} ms`}
          subtitle="Mean across benchmarked agents"
        />
        <StatisticCard
          title="Benchmark Executions"
          value={overview.total_executions}
          subtitle={`${overview.overall_success_rate.toFixed(1)}% success rate`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {overview.agents.map((agent) => (
          <div
            key={agent.agent_name}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {agent.agent_name}
                </h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  {agent.success_count}/{agent.total_executions} successful runs
                </p>
              </div>
              <span className={`text-2xl font-semibold ${scoreColor(agent.health_score)}`}>
                {agent.health_score}
              </span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-500 dark:text-slate-400">
              <div>Availability: {agent.availability}</div>
              <div>Reliability: {agent.reliability}</div>
              <div>Performance: {agent.performance}</div>
              <div>Accuracy: {agent.accuracy}</div>
            </div>
          </div>
        ))}
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="border-b border-slate-200 px-4 py-4 dark:border-slate-800">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
            Performance Table
          </h3>
        </div>
        <DataTable columns={tableColumns} data={overview.agents} />
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Latency Chart</h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Mean execution time per agent (ms)
          </p>
          <div className="mt-4">
            <BarChart
              items={overview.agents}
              maxValue={maxLatency}
              valueKey="mean_execution_time_ms"
              labelKey="agent_name"
            />
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
            AI vs Fallback Usage
          </h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Offline benchmark execution paths
          </p>
          <div className="mt-4 flex gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-indigo-500" /> AI
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-slate-400" /> Fallback
            </span>
          </div>
          <div className="mt-4">
            <UsageChart agents={overview.agents} />
          </div>
        </section>
      </div>
    </div>
  );
}
