import type { APIResponse, EvaluationOverview } from "../types/api";
import { apiClient } from "./apiClient";

export async function fetchEvaluationOverview(): Promise<EvaluationOverview> {
  const response = await apiClient.get<APIResponse<EvaluationOverview>>("/api/v1/evaluation");
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load evaluation overview");
  }
  return response.data.data;
}

export async function fetchAgentEvaluation(agentName: string): Promise<EvaluationOverview["agents"][number]> {
  const response = await apiClient.get<APIResponse<EvaluationOverview["agents"][number]>>(
    `/api/v1/evaluation/${encodeURIComponent(agentName)}`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load agent evaluation");
  }
  return response.data.data;
}
