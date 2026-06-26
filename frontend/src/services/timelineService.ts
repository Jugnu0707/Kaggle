import type { APIResponse, Severity } from "../types/api";
import { apiClient } from "./apiClient";

export type TimelineEventType =
  | "Alert"
  | "Process Execution"
  | "Authentication"
  | "Network"
  | "File"
  | "Registry"
  | "PowerShell"
  | "EDR"
  | "Firewall"
  | "User Action"
  | "AI Assessment";

export interface TimelineEvent {
  id: string | null;
  sequence: number;
  timestamp: string;
  source: string;
  event_type: TimelineEventType;
  severity: Severity;
  description: string;
  evidence_reference: string | null;
  confidence: number;
  timestamp_uncertain: boolean;
}

export interface TimelineResponse {
  incident_id: string;
  total_events: number;
  timeline: TimelineEvent[];
  investigation_summary: string;
}

export async function getIncidentTimeline(incidentId: string): Promise<TimelineResponse> {
  const response = await apiClient.get<APIResponse<TimelineResponse>>(
    `/api/v1/incidents/${incidentId}/timeline`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load investigation timeline");
  }
  return response.data.data;
}

export async function exportIncidentTimeline(
  incidentId: string,
  format: "json" | "markdown",
): Promise<Blob> {
  const response = await apiClient.get<Blob>(
    `/api/v1/incidents/${incidentId}/timeline/export?format=${format}`,
    { responseType: "blob" },
  );
  return response.data;
}
