import type { APIResponse, RiskAssessmentRecord } from "../types/api";
import { apiClient } from "./apiClient";

export async function getIncidentRiskAssessment(
  incidentId: string,
): Promise<RiskAssessmentRecord> {
  const response = await apiClient.get<APIResponse<RiskAssessmentRecord>>(
    `/api/v1/incidents/${incidentId}/risk`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load risk assessment");
  }
  return response.data.data;
}
