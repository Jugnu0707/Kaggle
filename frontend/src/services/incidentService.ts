import type {
  APIResponse,
  HealthData,
  IncidentDetail,
  IncidentList,
  Severity,
  IncidentStatus,
} from "../types/api";
import { apiClient } from "./apiClient";

export interface ListIncidentsParams {
  page?: number;
  page_size?: number;
  severity?: Severity;
  status?: IncidentStatus;
  search?: string;
}

export async function fetchHealth(): Promise<HealthData> {
  const response = await apiClient.get<APIResponse<HealthData>>("/api/v1/health");
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Health check failed");
  }
  return response.data.data;
}

export async function listIncidents(params: ListIncidentsParams = {}): Promise<IncidentList> {
  const response = await apiClient.get<APIResponse<IncidentList>>("/api/v1/incidents", {
    params,
  });
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load incidents");
  }
  return response.data.data;
}

export async function getIncident(incidentId: string): Promise<IncidentDetail> {
  const response = await apiClient.get<APIResponse<IncidentDetail>>(
    `/api/v1/incidents/${incidentId}`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Incident not found");
  }
  return response.data.data;
}
