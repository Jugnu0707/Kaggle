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
  timestamp: string;
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
