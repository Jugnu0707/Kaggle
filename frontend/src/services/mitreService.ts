import type { APIResponse, MitreFindingList } from "../types/api";
import { apiClient } from "./apiClient";

export async function getIncidentMitreMappings(incidentId: string): Promise<MitreFindingList> {
  const response = await apiClient.get<APIResponse<MitreFindingList>>(
    `/api/v1/incidents/${incidentId}/mitre`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load MITRE mappings");
  }
  return response.data.data;
}
