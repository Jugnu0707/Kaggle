import type { APIResponse } from "../types/api";
import { apiClient } from "./apiClient";

export interface InvestigationStageResult {
  agent: string;
  success: boolean;
  duration_ms: number;
  fallback_used: boolean;
  error: string | null;
}

export interface InvestigationPackage {
  execution_id: string;
  incident_id: string;
  status: "running" | "completed" | "partial" | "failed";
  duration_ms: number;
  overall_risk: string;
  agents_executed: string[];
  agents_completed: string[];
  agents_failed: string[];
  stages: InvestigationStageResult[];
  report_id: string | null;
  timeline_id: string | null;
  evaluation_score: number | null;
  started_at: string;
  completed_at: string | null;
}

export async function runInvestigation(incidentId: string): Promise<InvestigationPackage> {
  const response = await apiClient.post<APIResponse<InvestigationPackage>>(
    "/api/v1/investigations/run",
    { incident_id: incidentId },
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to run investigation");
  }
  return response.data.data;
}

export async function getInvestigationRun(runId: string): Promise<InvestigationPackage> {
  const response = await apiClient.get<APIResponse<InvestigationPackage>>(
    `/api/v1/investigations/runs/${runId}`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load investigation run");
  }
  return response.data.data;
}
