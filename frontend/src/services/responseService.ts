import type { APIResponse, ResponsePlanRecord } from "../types/api";
import { apiClient } from "./apiClient";

export async function getIncidentResponsePlan(
  incidentId: string,
): Promise<ResponsePlanRecord> {
  const response = await apiClient.get<APIResponse<ResponsePlanRecord>>(
    `/api/v1/incidents/${incidentId}/response`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load response plan");
  }
  return response.data.data;
}
