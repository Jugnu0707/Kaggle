import type { APIResponse, ExecutiveReportRecord } from "../types/api";
import { apiClient } from "./apiClient";

export async function getIncidentExecutiveReport(
  incidentId: string,
): Promise<ExecutiveReportRecord> {
  const response = await apiClient.get<APIResponse<ExecutiveReportRecord>>(
    `/api/v1/incidents/${incidentId}/executive-report`,
  );
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load executive report");
  }
  return response.data.data;
}

export async function generateExecutiveReport(
  incidentId: string,
): Promise<ExecutiveReportRecord> {
  const response = await apiClient.post<
    APIResponse<{
      source: "AI" | "FALLBACK";
      title: string;
      executive_summary: string;
      business_impact: string;
      key_findings: string[];
      recommended_actions: string[];
      lessons_learned: string[];
      markdown: string;
    }>
  >("/api/v1/agents/executive-report", {
    incident_id: incidentId,
  });
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to generate executive report");
  }
  const generated = response.data.data;
  return {
    id: incidentId,
    incident_id: incidentId,
    source: generated.source,
    title: generated.title,
    executive_summary: generated.executive_summary,
    business_impact: generated.business_impact,
    key_findings: generated.key_findings,
    recommended_actions: generated.recommended_actions,
    lessons_learned: generated.lessons_learned,
    markdown_report: generated.markdown,
    created_at: new Date().toISOString(),
  };
}
