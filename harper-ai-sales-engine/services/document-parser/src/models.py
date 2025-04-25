from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FieldExtraction(BaseModel):
    """Model for a field extracted from a document."""
    field_name: str
    value: Any
    confidence: float = Field(ge=0.0, le=1.0)


class DocumentMetadata(BaseModel):
    """Model for document metadata."""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: str
    parsed_timestamp: Optional[str] = None
    status: str = "pending"  # pending, uploaded, processing, parsed, failed
    error: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint."""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    parse_status: str
    message: str


class DocumentParseResponse(BaseModel):
    """Response model for document parsing endpoint."""
    document_id: str
    status: str
    extracted_fields: List[FieldExtraction] = []
    document_type: str = "unknown"
    summary: str = ""
    message: str


class ParseRequest(BaseModel):
    """Request model for document parsing endpoint."""
    fields: Optional[List[str]] = None
    extraction_level: str = Field(
        default="detailed", 
        description="Level of detail for extraction (basic, detailed, comprehensive)"
    )
    custom_instructions: Optional[str] = None


class InsuranceApplication(BaseModel):
    """Model for extracted insurance application data."""
    applicant_name: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    tax_id: Optional[str] = None
    annual_revenue: Optional[str] = None
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    coverage_types: List[str] = []
    existing_policies: List[Dict[str, Any]] = []
    claims_history: List[Dict[str, Any]] = []
    additional_info: Dict[str, Any] = {}


class InsurancePolicy(BaseModel):
    """Model for extracted insurance policy data."""
    policy_number: Optional[str] = None
    carrier: Optional[str] = None
    policy_type: Optional[str] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    premium: Optional[float] = None
    coverage_limits: Dict[str, Any] = {}
    deductibles: Dict[str, Any] = {}
    endorsements: List[Dict[str, Any]] = []
    exclusions: List[str] = []


class ClaimDocument(BaseModel):
    """Model for extracted insurance claim data."""
    claim_number: Optional[str] = None
    policy_number: Optional[str] = None
    claimant_name: Optional[str] = None
    incident_date: Optional[str] = None
    filing_date: Optional[str] = None
    incident_description: Optional[str] = None
    claim_amount: Optional[float] = None
    claim_status: Optional[str] = None
    adjuster: Optional[str] = None
    supporting_documents: List[str] = []
