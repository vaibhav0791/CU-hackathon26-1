"""
Pydantic models for Clinical Trial Analysis API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AdverseEvent(BaseModel):
    """Adverse event data"""
    event: str
    count: int
    severity: str  # Mild, Moderate, Serious


class Eligibility(BaseModel):
    """Trial eligibility criteria"""
    age_min: int
    age_max: int
    gender: str
    accepts_healthy_volunteers: bool


class ClinicalTrial(BaseModel):
    """ClinicalTrials.gov trial data"""
    nct_id: str
    title: str
    status: str
    phase: str
    study_type: str
    condition: List[str]
    intervention: List[str]
    sponsor: str
    location: List[str]
    enrollment: int
    start_date: str
    estimated_completion_date: str
    primary_outcome: str
    secondary_outcomes: List[str]
    adverse_events: List[AdverseEvent]
    eligibility: Eligibility


class VitalSigns(BaseModel):
    """Patient vital signs"""
    heart_rate: int
    blood_pressure: str
    respiratory_rate: int
    temperature: float
    oxygen_saturation: int


class LabResults(BaseModel):
    """Patient lab results"""
    white_blood_cell_count: Optional[float] = None
    hemoglobin: Optional[float] = None
    creatinine: Optional[float] = None
    lactate: Optional[float] = None
    troponin: Optional[float] = None
    brain_natriuretic_peptide: Optional[float] = None
    ejection_fraction: Optional[float] = None
    amylase: Optional[float] = None
    lipase: Optional[float] = None
    blood_urea_nitrogen: Optional[float] = None


class MIMICPatient(BaseModel):
    """MIMIC-III ICU patient data"""
    patient_id: str
    admission_id: str
    age: int
    gender: str
    icu_stay_duration_days: int
    diagnosis: List[str]
    vital_signs: VitalSigns
    lab_results: LabResults
    medications: List[str]
    procedures: List[str]
    outcome: str
    mortality_risk_score: float


class Intervention(BaseModel):
    """Trial intervention"""
    intervention_type: str
    intervention_name: str
    description: str


class Outcome(BaseModel):
    """Trial outcome"""
    outcome: str
    timeframe: str
    description: Optional[str] = None


class Location(BaseModel):
    """Trial location"""
    facility: str
    status: str
    country: str


class AdverseEventStructured(BaseModel):
    """Structured adverse event from AACT"""
    event_term: str
    organ_system: str
    adverse_event_count: int
    serious_adverse_event: bool


class Enrollment(BaseModel):
    """Enrollment information"""
    value: int
    type: str


class DateInfo(BaseModel):
    """Date information"""
    date: str
    type: str


class AACTTrial(BaseModel):
    """AACT structured trial data"""
    nct_id: str
    title: str
    brief_summary: str
    official_title: str
    phase: str
    status: str
    study_type: str
    design_allocation: str
    design_intervention_model: str
    design_primary_purpose: str
    enrollment: Enrollment
    start_date: DateInfo
    completion_date: DateInfo
    last_update_posted: str
    results_first_posted: Optional[str]
    conditions: List[str]
    interventions: List[Intervention]
    outcomes: Dict[str, List[Outcome]]
    adverse_events_reported: List[AdverseEventStructured]
    locations: List[Location]


class TrialOutcomesAnalysis(BaseModel):
    """Trial outcomes analysis"""
    nct_id: str
    trial_title: str
    status: str
    primary_outcomes: str
    secondary_outcomes: List[str]
    adverse_events_summary: Dict[str, Any]
    enrollment_info: Dict[str, Any]


class ClinicalTrialSearchRequest(BaseModel):
    """Clinical trial search request"""
    query: str = Field(..., description="Search query (title, condition, etc.)")
    phase: Optional[str] = Field(None, description="Filter by phase")
    status: Optional[str] = Field(None, description="Filter by status")