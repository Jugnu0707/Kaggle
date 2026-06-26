import type { APIResponse, GuardianAuditList } from "../types/api";
import { apiClient } from "./apiClient";

export async function getIncidentGuardianAudits(
  incidentId: string,
): Promise<GuardianAuditList> {
  const response = await apiClient.get<APIResponse<GuardianAuditList>>(
    `/api/v1/incidents/${incidentId}/guardian-audits`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load Guardian audit records");
  }
  return response.data.data;
}
