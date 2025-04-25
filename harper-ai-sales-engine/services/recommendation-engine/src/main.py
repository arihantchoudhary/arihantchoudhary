import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, HTTPException, Body, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("recommendation-engine")

# Create FastAPI app
app = FastAPI(
    title="Harper Insurance Carrier Recommendation Engine",
    description="AI-driven recommendation system for insurance carrier selection",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class BusinessProfile(BaseModel):
    """Business profile used for carrier recommendations."""
    business_name: str
    business_type: str
    industry: str
    annual_revenue: float
    employee_count: int
    years_in_business: int
    location: str
    coverage_needs: List[str]
    has_previous_claims: bool = False
    previous_claims_count: int = 0
    previous_claims_amount: float = 0
    risk_factors: Optional[List[str]] = None
    coverage_amount: Optional[float] = None
    deductible_preference: Optional[str] = None
    premium_budget: Optional[float] = None
    custom_features: Optional[Dict[str, Any]] = None


class CarrierMatch(BaseModel):
    """A carrier match with confidence score and details."""
    carrier_id: str
    carrier_name: str
    match_score: float
    estimated_premium: Optional[float] = None
    specializations: List[str]
    coverage_details: Dict[str, Any]
    strengths: List[str]
    limitations: List[str]
    submission_requirements: List[str]


class RecommendationResponse(BaseModel):
    """Response model for carrier recommendations."""
    business_id: str
    recommended_carriers: List[CarrierMatch]
    request_id: str
    processing_time_ms: float
    recommendations_generated_at: str
    explanation: Optional[str] = None


class CarrierSubmissionRequest(BaseModel):
    """Request model for submitting to carriers."""
    business_id: str
    carrier_ids: List[str]
    application_data: Dict[str, Any]
    documents: List[str]
    priority: str = "normal"  # normal, high, urgent


class CarrierSubmissionResponse(BaseModel):
    """Response model for carrier submission."""
    submission_id: str
    business_id: str
    carrier_ids: List[str]
    status: str
    submission_timestamp: str
    estimated_response_time: Optional[str] = None
    message: str


# Mock carrier data (in production, this would come from a database)
MOCK_CARRIERS = [
    {
        "id": "CAR001",
        "name": "InsureTech Underwriters",
        "specializations": ["technology", "professional_services", "startups"],
        "min_revenue": 500000,
        "max_revenue": 50000000,
        "coverage_types": ["general_liability", "cyber", "professional_liability", "property"],
        "rating": 4.7,
        "response_time_days": 3,
        "strengths": ["Fast quote turnaround", "Specialized coverage for tech risks", "Competitive cyber premiums"],
        "limitations": ["Limited coverage for manufacturing", "Higher premiums for companies with previous claims"],
        "regions": ["CA", "NY", "TX", "MA", "WA", "CO"],
        "requirements": ["Business financials", "Security questionnaire for cyber coverage"]
    },
    {
        "id": "CAR002",
        "name": "Heritage Insurance Group",
        "specializations": ["retail", "hospitality", "real_estate"],
        "min_revenue": 250000,
        "max_revenue": 100000000,
        "coverage_types": ["general_liability", "property", "business_interruption", "workers_comp"],
        "rating": 4.5,
        "response_time_days": 5,
        "strengths": ["Comprehensive property coverage", "Flexible payment terms", "Established claims process"],
        "limitations": ["Slower quote turnaround", "Less competitive for technology risks"],
        "regions": ["All US states"],
        "requirements": ["Business license", "Property details", "Loss runs"]
    },
    {
        "id": "CAR003",
        "name": "Apex Risk Solutions",
        "specializations": ["healthcare", "manufacturing", "construction"],
        "min_revenue": 1000000,
        "max_revenue": 500000000,
        "coverage_types": ["general_liability", "professional_liability", "workers_comp", "product_liability"],
        "rating": 4.8,
        "response_time_days": 4,
        "strengths": ["Industry-specific coverage options", "Risk management services included", "Flexible underwriting"],
        "limitations": ["Higher premiums", "Strict eligibility requirements"],
        "regions": ["CA", "TX", "FL", "IL", "PA", "NY", "OH", "MI"],
        "requirements": ["Detailed business operations", "Safety protocols", "Claims history"]
    },
    {
        "id": "CAR004",
        "name": "Velocity Insurance Partners",
        "specializations": ["technology", "fintech", "e-commerce"],
        "min_revenue": 100000,
        "max_revenue": 20000000,
        "coverage_types": ["general_liability", "cyber", "professional_liability", "d&o"],
        "rating": 4.6,
        "response_time_days": 2,
        "strengths": ["Digital-first approach", "Fast online quotes", "Specialized startup packages"],
        "limitations": ["Limited coverage for physical assets", "Less robust for larger businesses"],
        "regions": ["CA", "NY", "MA", "WA", "TX", "CO", "GA", "IL"],
        "requirements": ["Digital application only", "API integration available"]
    },
    {
        "id": "CAR005",
        "name": "Guardian Commercial Coverage",
        "specializations": ["manufacturing", "distribution", "wholesale", "logistics"],
        "min_revenue": 2000000,
        "max_revenue": 250000000,
        "coverage_types": ["general_liability", "property", "business_interruption", "marine", "auto"],
        "rating": 4.4,
        "response_time_days": 6,
        "strengths": ["Supply chain coverage options", "International shipping protection", "Fleet discounts"],
        "limitations": ["Longer quote process", "Limited tech industry expertise"],
        "regions": ["All US states", "International capabilities"],
        "requirements": ["Business financial statements", "Fleet details if applicable", "Shipping volume data"]
    }
]


def match_carriers(business_profile: BusinessProfile) -> List[CarrierMatch]:
    """
    Match business profile with appropriate carriers.
    
    This would be a sophisticated ML model in production.
    """
    matches = []
    business_industry = business_profile.industry.lower()
    business_type = business_profile.business_type.lower()
    business_revenue = business_profile.annual_revenue
    
    for carrier in MOCK_CARRIERS:
        # Basic filtering
        if business_revenue < carrier["min_revenue"] or business_revenue > carrier["max_revenue"]:
            continue
            
        # Calculate base match score
        match_score = 0.5  # Start with neutral score
        
        # Industry match
        if business_industry in carrier["specializations"] or business_type in carrier["specializations"]:
            match_score += 0.3
        
        # Coverage match
        coverage_match_count = sum(1 for coverage in business_profile.coverage_needs 
                                   if coverage in carrier["coverage_types"])
        coverage_match_ratio = coverage_match_count / len(business_profile.coverage_needs) if business_profile.coverage_needs else 0
        match_score += (coverage_match_ratio * 0.2)
        
        # Location match
        if "All US states" in carrier["regions"] or business_profile.location in carrier["regions"]:
            match_score += 0.1
        
        # Risk adjustment
        if business_profile.has_previous_claims and business_profile.previous_claims_count > 2:
            match_score -= 0.1
        
        # Cap the score between 0 and 1
        match_score = max(0.1, min(0.99, match_score))
        
        # Calculate estimated premium (simplified)
        base_premium = business_revenue * 0.005  # 0.5% of revenue as base
        industry_factor = 1.2 if business_industry in ["technology", "healthcare"] else 1.0
        claims_factor = 1.3 if business_profile.has_previous_claims else 1.0
        size_factor = 0.8 if business_profile.employee_count < 10 else (
            1.0 if business_profile.employee_count < 50 else 1.2
        )
        estimated_premium = base_premium * industry_factor * claims_factor * size_factor
        
        # Create match object
        match = CarrierMatch(
            carrier_id=carrier["id"],
            carrier_name=carrier["name"],
            match_score=match_score,
            estimated_premium=estimated_premium,
            specializations=carrier["specializations"],
            coverage_details={
                "types": carrier["coverage_types"],
                "rating": carrier["rating"],
                "response_time_days": carrier["response_time_days"]
            },
            strengths=carrier["strengths"],
            limitations=carrier["limitations"],
            submission_requirements=carrier["requirements"]
        )
        
        matches.append(match)
    
    # Sort by match score, descending
    matches.sort(key=lambda x: x.match_score, reverse=True)
    
    return matches


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "recommendation-engine"}


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_carriers(business_profile: BusinessProfile):
    """
    Recommend insurance carriers based on business profile.
    """
    try:
        # Generate a unique request ID
        request_id = f"req_{int(datetime.now().timestamp() * 1000)}"
        business_id = f"bus_{business_profile.business_name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        # Record start time for performance tracking
        start_time = datetime.now()
        
        # Get carrier matches
        carrier_matches = match_carriers(business_profile)
        
        # Generate explanation
        explanation = f"Found {len(carrier_matches)} carriers matching {business_profile.business_type} businesses in the {business_profile.industry} industry with {business_profile.coverage_needs} coverage needs."
        
        # Calculate processing time
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log the recommendation
        logger.info(f"Generated recommendations for {business_profile.business_name} with {len(carrier_matches)} matches")
        
        return RecommendationResponse(
            business_id=business_id,
            recommended_carriers=carrier_matches,
            request_id=request_id,
            processing_time_ms=processing_time_ms,
            recommendations_generated_at=datetime.now().isoformat(),
            explanation=explanation
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@app.post("/submit", response_model=CarrierSubmissionResponse)
async def submit_to_carriers(request: CarrierSubmissionRequest):
    """
    Submit application to selected carriers.
    """
    try:
        # Generate a unique submission ID
        submission_id = f"sub_{int(datetime.now().timestamp() * 1000)}"
        
        # In production, this would initiate the actual submission process to carriers
        # For now, we'll mock the response
        
        # Calculate estimated response time based on priority
        if request.priority == "urgent":
            est_response_days = 1
        elif request.priority == "high":
            est_response_days = 3
        else:
            est_response_days = 5
            
        # Get carrier names for logging
        carrier_names = []
        for carrier_id in request.carrier_ids:
            for carrier in MOCK_CARRIERS:
                if carrier["id"] == carrier_id:
                    carrier_names.append(carrier["name"])
                    break
        
        # Create response
        response = CarrierSubmissionResponse(
            submission_id=submission_id,
            business_id=request.business_id,
            carrier_ids=request.carrier_ids,
            status="submitted",
            submission_timestamp=datetime.now().isoformat(),
            estimated_response_time=f"{est_response_days} business days",
            message=f"Application submitted to {len(request.carrier_ids)} carriers: {', '.join(carrier_names)}"
        )
        
        # Log the submission
        logger.info(f"Application for {request.business_id} submitted to carriers: {', '.join(carrier_names)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error submitting to carriers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting to carriers: {str(e)}")


@app.get("/carriers")
async def list_carriers():
    """Get a list of all available carriers."""
    return {"carriers": MOCK_CARRIERS}


@app.get("/carriers/{carrier_id}")
async def get_carrier_details(carrier_id: str):
    """Get details for a specific carrier."""
    for carrier in MOCK_CARRIERS:
        if carrier["id"] == carrier_id:
            return carrier
    
    raise HTTPException(status_code=404, detail=f"Carrier with ID {carrier_id} not found")


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3004"))
    reload = os.getenv("RELOAD", "True").lower() in ("true", "1", "t")
    
    # Start the API server
    import uvicorn
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
