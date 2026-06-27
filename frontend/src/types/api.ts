export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
}

export type Severity = "Critical" | "High" | "Medium" | "Low";
export type IncidentStatus = "New" | "Investigating" | "Resolved" | "Closed";
export type UploadStatus = "Completed" | "Deleted" | "Failed";

export interface HealthData {
  status: string;
  application_name: string;
  version: string;
  uptime_seconds: number;
  database_connected: boolean;
  adk?: boolean;
  coordinator?: boolean;
  mcp?: boolean;
  runtime?: boolean;
  registered_agents?: number;
  registered_tools?: number;
  timestamp: string;
}

export interface MCPStatusData {
  mcp: boolean;
  tool_count: number;
  tools: string[];
}

export interface DashboardStats {
  total_incidents: number;
  critical_incidents: number;
  high_incidents: number;
  uploaded_logs: number;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: IncidentStatus;
  source: string;
  confidence_score: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface Investigation {
  id: string;
  incident_id: string;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  investigation_status: string;
}

export interface IncidentDetail extends Incident {
  investigation: Investigation | null;
  evidence_count: number;
}

export interface IncidentList {
  items: Incident[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LogUploadResult {
  file_id: string;
  filename: string;
  size: number;
  upload_timestamp: string;
}

export interface LogFileMetadata {
  id: string;
  incident_id: string | null;
  original_filename: string;
  stored_filename: string;
  file_extension: string;
  mime_type: string;
  file_size_bytes: number;
  upload_status: UploadStatus;
  uploaded_at: string;
  storage_path: string;
  checksum_sha256: string;
  deleted_at: string | null;
}

export interface LogFileList {
  items: LogFileMetadata[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MitreFinding {
  id: string;
  incident_id: string;
  technique_id: string;
  technique_name: string;
  tactic: string;
  confidence: number;
  evidence: string[];
  created_at: string;
}

export interface MitreFindingList {
  items: MitreFinding[];
  total: number;
}

export interface RiskAssessmentRecord {
  id: string;
  incident_id: string;
  source: "AI" | "FALLBACK";
  overall_risk: Severity;
  risk_score: number;
  likelihood: string;
  business_impact: string;
  confidence: number;
  priority: string;
  summary: string;
  reasoning: string;
  created_at: string;
}

export interface ResponsePlanRecord {
  id: string;
  incident_id: string;
  source: "AI" | "FALLBACK";
  priority: string;
  containment: string[];
  eradication: string[];
  recovery: string[];
  monitoring: string[];
  executive_summary: string;
  created_at: string;
}

export interface ExecutiveReportRecord {
  id: string;
  incident_id: string;
  source: "AI" | "FALLBACK";
  title: string;
  executive_summary: string;
  business_impact: string;
  key_findings: string[];
  recommended_actions: string[];
  lessons_learned: string[];
  markdown_report: string;
  created_at: string;
}

export interface GuardianAuditRecord {
  id: string;
  incident_id: string | null;
  agent_name: string;
  validation_status: "approved" | "warning" | "rejected";
  issues_found: string[];
  action_taken: string;
  created_at: string;
}

export interface GuardianAuditList {
  items: GuardianAuditRecord[];
  total: number;
}

export type ThreatReputation =
  | "Malicious"
  | "Suspicious"
  | "Unknown"
  | "Safe"
  | "Informational";

export interface ThreatIntelligenceFindingRecord {
  id: string;
  incident_id: string;
  indicator: string;
  indicator_type: string;
  reputation: ThreatReputation;
  confidence: number;
  source: "AI" | "FALLBACK";
  description: string;
  analyst_notes: string;
  created_at: string;
}

export interface ThreatIntelligenceFindingList {
  items: ThreatIntelligenceFindingRecord[];
  total: number;
}

export interface AgentEvaluationSummary {
  agent_name: string;
  health_score: number;
  availability: number;
  reliability: number;
  performance: number;
  accuracy: number;
  total_executions: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  mean_execution_time_ms: number;
  ai_used_count: number;
  fallback_used_count: number;
  mean_confidence: number | null;
  mean_retry_count: number;
  mean_output_size: number;
}

export interface EvaluationOverview {
  overall_score: number;
  agents: AgentEvaluationSummary[];
  total_executions: number;
  overall_success_rate: number;
  generated_at: string | null;
  tool_execution_count: number;
  tool_failure_count: number;
  mean_adk_session_duration_ms: number;
  mean_investigation_duration_ms: number;
  mean_agent_execution_time_ms: number;
  mean_mcp_latency_ms: number;
}
