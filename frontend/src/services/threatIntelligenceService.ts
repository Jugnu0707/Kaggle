import type { APIResponse, ThreatIntelligenceFindingList } from "../types/api";
import { apiClient } from "./apiClient";

export async function getIncidentThreatIntelligence(
  incidentId: string,
): Promise<ThreatIntelligenceFindingList> {
  const response = await apiClient.get<APIResponse<ThreatIntelligenceFindingList>>(
    `/api/v1/incidents/${incidentId}/threat-intelligence`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load threat intelligence findings");
  }
  return response.data.data;
}
