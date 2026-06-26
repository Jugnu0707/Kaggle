"""Agent orchestration API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.evidence_agent import EvidenceCollectRequest, EvidenceCollectResponse
from app.schemas.orchestration import OrchestrateRequest, OrchestrateResponse
from app.schemas.response import APIResponse
from app.schemas.response_agent import ResponsePlanRequest, ResponsePlanResponse
from app.schemas.risk_agent import RiskAssessmentRequest, RiskAssessmentResponse
from app.schemas.threat_intelligence_agent import (
    ThreatIntelligenceRequest,
    ThreatIntelligenceResponse,
)
from app.schemas.mitre_agent import MitreMappingRequest, MitreMappingResponse
from app.services.evidence_agent_service import EvidenceAgentService
from app.services.mitre_agent_service import MitreAgentService
from app.services.orchestration_service import OrchestrationService
from app.services.response_agent_service import ResponseAgentService
from app.services.risk_agent_service import RiskAgentService
from app.services.threat_intelligence_agent_service import ThreatIntelligenceAgentService

router = APIRouter(prefix="/agents", tags=["agents"])


def get_orchestration_service(db: Session = Depends(get_db)) -> OrchestrationService:
    """Provide an orchestration service bound to the request database session."""
    return OrchestrationService(db)


def get_evidence_agent_service(db: Session = Depends(get_db)) -> EvidenceAgentService:
    """Provide an Evidence Agent service bound to the request database session."""
    return EvidenceAgentService(db)


@router.post(
    "/evidence",
    response_model=APIResponse[EvidenceCollectResponse],
    status_code=status.HTTP_200_OK,
    summary="Collect incident evidence",
    description=(
        "Collect, validate, normalize, and summarize evidence from an uploaded "
        "log file for an incident. No threat analysis or LLM reasoning is performed."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Evidence collected successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Evidence collected",
                        "data": {
                            "status": "completed",
                            "evidence_summary": {
                                "file_type": "application_log",
                                "total_entries": 3,
                                "time_range": "2026-06-26T10:00:00 to 2026-06-26T11:00:00",
                                "possible_log_source": "Generic application log",
                                "data_quality_observations": [
                                    "Sample entries are available for review",
                                    "Timestamps detected in log entries",
                                ],
                            },
                            "evidence_package": {
                                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "uploaded_file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                                "file_size": 256,
                                "number_of_lines": 3,
                                "detected_log_type": "application_log",
                                "sample_entries": [
                                    "2026-06-26T10:00:00 ERROR process started"
                                ],
                                "collection_timestamp": "2026-06-26T12:00:00Z",
                            },
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident or log file not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
def collect_evidence(
    payload: EvidenceCollectRequest,
    service: EvidenceAgentService = Depends(get_evidence_agent_service),
) -> APIResponse[EvidenceCollectResponse]:
    """Collect and summarize evidence from an uploaded log file."""
    result = service.collect(payload)
    return APIResponse(
        success=True,
        message="Evidence collected",
        data=result,
    )


def get_threat_intelligence_agent_service(
    db: Session = Depends(get_db),
) -> ThreatIntelligenceAgentService:
    """Provide a Threat Intelligence Agent service bound to the request database session."""
    return ThreatIntelligenceAgentService(db)


@router.post(
    "/threat-intelligence",
    response_model=APIResponse[ThreatIntelligenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Enrich evidence with threat intelligence",
    description=(
        "Extract and enrich indicators of compromise from incident evidence. "
        "Uses Gemini when available and automatically falls back to the offline "
        "reputation engine when AI is unavailable. Enrichment only — never blocks "
        "or quarantines."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Threat intelligence enrichment completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Threat intelligence enrichment completed",
                        "data": {
                            "status": "completed",
                            "ioc_count": 2,
                            "findings": [
                                {
                                    "indicator": "185.234.72.19",
                                    "indicator_type": "IPv4",
                                    "reputation": "Unknown",
                                    "confidence": 85,
                                    "source": "FALLBACK",
                                    "description": "Public IPv4 address requires analyst review",
                                    "analyst_notes": "Offline enrichment applied.",
                                }
                            ],
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident not found"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
    },
)
def enrich_threat_intelligence(
    payload: ThreatIntelligenceRequest,
    service: ThreatIntelligenceAgentService = Depends(get_threat_intelligence_agent_service),
) -> APIResponse[ThreatIntelligenceResponse]:
    """Extract IOCs and generate a threat intelligence report."""
    result = service.enrich(payload)
    return APIResponse(
        success=True,
        message="Threat intelligence enrichment completed",
        data=result,
    )


def get_mitre_agent_service(db: Session = Depends(get_db)) -> MitreAgentService:
    """Provide a MITRE Mapping Agent service bound to the request database session."""
    return MitreAgentService(db)


@router.post(
    "/mitre",
    response_model=APIResponse[MitreMappingResponse],
    status_code=status.HTTP_200_OK,
    summary="Map evidence to MITRE ATT&CK",
    description=(
        "Map normalized evidence from an incident to MITRE ATT&CK techniques using "
        "local rule-based matching. No external APIs or LLM reasoning are used."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "MITRE mapping completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "MITRE mapping completed",
                        "data": {
                            "status": "completed",
                            "techniques": [
                                {
                                    "technique_id": "T1059.001",
                                    "technique_name": "PowerShell",
                                    "tactic": "Execution",
                                    "confidence": 96,
                                    "matched_evidence": ["powershell.exe"],
                                }
                            ],
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident not found"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
    },
)
def map_mitre_techniques(
    payload: MitreMappingRequest,
    service: MitreAgentService = Depends(get_mitre_agent_service),
) -> APIResponse[MitreMappingResponse]:
    """Map incident evidence to MITRE ATT&CK techniques."""
    result = service.map_incident(payload)
    return APIResponse(
        success=True,
        message="MITRE mapping completed",
        data=result,
    )


def get_risk_agent_service(db: Session = Depends(get_db)) -> RiskAgentService:
    """Provide a Risk Assessment Agent service bound to the request database session."""
    return RiskAgentService(db)


@router.post(
    "/risk",
    response_model=APIResponse[RiskAssessmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Assess incident risk",
    description=(
        "Produce a structured enterprise risk assessment from incident, evidence, "
        "MITRE, and threat intelligence inputs. Uses Gemini when available and "
        "automatically falls back to deterministic rules when AI is unavailable."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Risk assessment completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Risk assessment completed",
                        "data": {
                            "source": "FALLBACK",
                            "overall_risk": "High",
                            "risk_score": 80,
                            "likelihood": "Likely",
                            "business_impact": "Significant business disruption",
                            "confidence": 85,
                            "priority": "P2",
                            "summary": "Fallback risk assessment classified the incident as High.",
                            "reasoning": "Incident severity is High",
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident not found"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
    },
)
def assess_risk(
    payload: RiskAssessmentRequest,
    service: RiskAgentService = Depends(get_risk_agent_service),
) -> APIResponse[RiskAssessmentResponse]:
    """Assess enterprise risk for an incident."""
    result = service.assess(payload)
    return APIResponse(
        success=True,
        message="Risk assessment completed",
        data=result,
    )


def get_response_agent_service(db: Session = Depends(get_db)) -> ResponseAgentService:
    """Provide a Response Planning Agent service bound to the request database session."""
    return ResponseAgentService(db)


@router.post(
    "/response",
    response_model=APIResponse[ResponsePlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate incident response plan",
    description=(
        "Produce a structured incident response plan from incident, evidence, "
        "MITRE, threat intelligence, and risk assessment inputs. Uses Gemini when "
        "available and automatically falls back to deterministic playbooks when AI "
        "is unavailable. Recommendations only — never executes remediation."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Response plan generated",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Response plan generated",
                        "data": {
                            "source": "FALLBACK",
                            "priority": "P2",
                            "containment": ["Isolate affected endpoint"],
                            "eradication": ["Block unauthorized PowerShell execution"],
                            "recovery": ["Validate endpoint integrity before reconnection"],
                            "monitoring": ["Monitor for repeated script execution"],
                            "executive_summary": "Fallback response plan for suspicious PowerShell activity.",
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident not found"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
    },
)
def plan_response(
    payload: ResponsePlanRequest,
    service: ResponseAgentService = Depends(get_response_agent_service),
) -> APIResponse[ResponsePlanResponse]:
    """Generate an incident response plan."""
    result = service.plan(payload)
    return APIResponse(
        success=True,
        message="Response plan generated",
        data=result,
    )


@router.post(
    "/orchestrate",
    response_model=APIResponse[OrchestrateResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate orchestration plan",
    description=(
        "Accept an incident ID or uploaded log ID, validate the request, invoke "
        "the Evidence Agent when a log file is present, invoke the MITRE Mapping "
        "Agent on the resulting evidence package, invoke the Threat Intelligence "
        "Agent on the same evidence package, invoke the Risk Assessment Agent, "
        "invoke the Response Planning Agent, and return a structured orchestration "
        "plan. Remaining specialist agents are placeholders."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Orchestration plan generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Orchestration plan generated",
                        "data": {
                            "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "log_id": None,
                            "workflow_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                            "status": "accepted",
                            "workflow": [
                                "Evidence Agent",
                                "Threat Intelligence Agent",
                                "MITRE Mapping Agent",
                                "Risk Assessment Agent",
                                "Response Planning Agent",
                                "Executive Report Agent",
                                "Guardian Agent",
                            ],
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident or log file not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
def orchestrate_agents(
    payload: OrchestrateRequest,
    service: OrchestrationService = Depends(get_orchestration_service),
) -> APIResponse[OrchestrateResponse]:
    """Generate a Coordinator orchestration plan for an incident or log."""
    plan = service.orchestrate(payload)
    return APIResponse(
        success=True,
        message="Orchestration plan generated",
        data=plan,
    )
