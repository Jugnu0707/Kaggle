import type { APIResponse } from "../types/api";
import { apiClient } from "./apiClient";

export interface ReplayStepExplainability {
  decision: string;
  reason: string;
  confidence: number | null;
  evidence_used: string[];
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  execution_time_ms: number;
  source: "AI" | "FALLBACK" | "SYSTEM";
}

export interface InvestigationReplayStep {
  step: number;
  agent: string;
  duration_ms: number;
  source: "AI" | "FALLBACK" | "SYSTEM";
  summary: string;
  confidence: number | null;
  status: string;
  fallback_used: boolean;
  started_at: string | null;
  completed_at: string | null;
  explainability: ReplayStepExplainability | null;
}

export interface InvestigationReplay {
  run_id: string;
  incident_id: string;
  status: string;
  duration_ms: number;
  steps: InvestigationReplayStep[];
}

export interface DecisionChainItem {
  step: number;
  agent: string;
  decision: string;
  reason: string;
  confidence: number | null;
  source: "AI" | "FALLBACK" | "SYSTEM";
}

export interface ConfidenceDistribution {
  min_confidence: number | null;
  max_confidence: number | null;
  average_confidence: number | null;
  steps_with_confidence: number;
}

export interface InvestigationExplain {
  run_id: string;
  incident_id: string;
  status: string;
  overall_investigation_summary: string;
  overall_risk: string;
  ai_usage_count: number;
  fallback_usage_count: number;
  system_steps_count: number;
  decision_chain: DecisionChainItem[];
  agent_reasoning: ReplayStepExplainability[];
  confidence_distribution: ConfidenceDistribution;
  evaluation_score: number | null;
  duration_ms: number;
}

export interface InvestigationReplayExport {
  format: "json" | "markdown";
  content: string;
  run_id: string;
}

export async function getInvestigationReplay(runId: string): Promise<InvestigationReplay> {
  const response = await apiClient.get<APIResponse<InvestigationReplay>>(
    `/api/v1/investigations/${runId}/replay`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load investigation replay");
  }
  return response.data.data;
}

export async function getInvestigationExplain(runId: string): Promise<InvestigationExplain> {
  const response = await apiClient.get<APIResponse<InvestigationExplain>>(
    `/api/v1/investigations/${runId}/explain`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load explainability data");
  }
  return response.data.data;
}

export async function exportInvestigationReplay(
  runId: string,
  format: "json" | "markdown",
): Promise<InvestigationReplayExport> {
  const response = await apiClient.get<APIResponse<InvestigationReplayExport>>(
    `/api/v1/investigations/${runId}/replay/export`,
    { params: { format } },
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to export replay");
  }
  return response.data.data;
}
