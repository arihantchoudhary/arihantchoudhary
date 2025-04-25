import os
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, HTTPException, Body, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import uvicorn
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("lead-scoring")

# Create FastAPI app
app = FastAPI(
    title="Harper Lead Scoring Engine",
    description="Lead scoring and prioritization service for the insurance sales pipeline",
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
class LeadFeatures(BaseModel):
    """Features used to score a lead."""
    business_name: str
    business_type: str
    annual_revenue: float
    employee_count: int
    industry: str
    location: str
    years_in_business: int
    website_available: bool = True
    previous_insurance: bool = False
    previous_claims_count: int = 0
    referral_source: Optional[str] = None
    contacted_before: bool = False
    initial_interest_level: Optional[int] = Field(None, ge=1, le=10, description="Scale of 1-10")
    time_spent_on_website: Optional[int] = None  # in seconds
    pages_visited: Optional[int] = None
    quote_form_started: bool = False
    quote_form_completed: bool = False
    custom_features: Optional[Dict[str, Any]] = None


class LeadScore(BaseModel):
    """Score and insights for a lead."""
    lead_id: str
    score: float
    conversion_probability: float
    priority: str  # high, medium, low
    estimated_premium: Optional[float] = None
    estimated_close_time_days: Optional[int] = None
    key_factors: List[Dict[str, Any]]
    segment: str
    recommended_actions: List[str]
    scored_at: str


class LeadScoringRequest(BaseModel):
    """Request for scoring multiple leads."""
    leads: List[Dict[str, Any]]
    include_explanations: bool = True


class LeadScoringResponse(BaseModel):
    """Response for scoring multiple leads."""
    results: List[LeadScore]
    processing_time_ms: float


# Mock implementations (would be real ML models in production)
def predict_conversion_probability(features: Dict[str, Any]) -> float:
    """Predict probability of conversion for a lead."""
    # This would be a real ML model in production
    base_probability = 0.3
    
    # Adjust based on business type
    business_type_factors = {
        "retail": 0.1,
        "technology": 0.15,
        "manufacturing": 0.05,
        "healthcare": 0.12,
        "construction": 0.08,
        "professional_services": 0.13,
    }
    business_type = features.get("business_type", "").lower()
    business_factor = business_type_factors.get(business_type, 0)
    
    # Adjust based on revenue and employees
    revenue = features.get("annual_revenue", 0)
    if revenue > 5000000:
        revenue_factor = 0.15
    elif revenue > 1000000:
        revenue_factor = 0.1
    elif revenue > 500000:
        revenue_factor = 0.05
    else:
        revenue_factor = 0
        
    # Engagement factors
    engagement_factor = 0
    if features.get("quote_form_completed", False):
        engagement_factor += 0.2
    elif features.get("quote_form_started", False):
        engagement_factor += 0.1
    
    if features.get("time_spent_on_website", 0) > 300:  # More than 5 minutes
        engagement_factor += 0.05
        
    # Previous relationship factors
    relationship_factor = 0
    if features.get("previous_insurance", False):
        relationship_factor += 0.05
    if features.get("contacted_before", False):
        relationship_factor += 0.03
        
    # Calculate final probability
    probability = base_probability + business_factor + revenue_factor + engagement_factor + relationship_factor
    
    # Cap between 0.01 and 0.99
    return max(0.01, min(0.99, probability))


def predict_premium_value(features: Dict[str, Any]) -> float:
    """Predict estimated premium value for a lead."""
    # This would be a real ML model in production
    base_premium = 5000
    
    # Adjust based on business type
    business_type_factors = {
        "retail": 1.2,
        "technology": 1.5,
        "manufacturing": 2.0,
        "healthcare": 1.8,
        "construction": 2.2,
        "professional_services": 1.3,
    }
    business_type = features.get("business_type", "").lower()
    business_factor = business_type_factors.get(business_type, 1.0)
    
    # Adjust based on revenue
    revenue = features.get("annual_revenue", 0)
    revenue_factor = (revenue / 1000000) * 0.5  # $0.5 per $1M of revenue
    
    # Adjust based on employees
    employee_count = features.get("employee_count", 0)
    employee_factor = employee_count * 10  # $10 per employee
    
    # Risk factors
    risk_factor = 1.0
    if features.get("previous_claims_count", 0) > 0:
        risk_factor = 1.2
    
    # Calculate final premium
    premium = (base_premium + revenue_factor + employee_factor) * business_factor * risk_factor
    
    return premium


def determine_priority(score: float) -> str:
    """Determine priority level based on score."""
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    else:
        return "low"


def determine_segment(features: Dict[str, Any]) -> str:
    """Determine customer segment based on features."""
    revenue = features.get("annual_revenue", 0)
    employee_count = features.get("employee_count", 0)
    business_type = features.get("business_type", "").lower()
    
    if revenue > 5000000 or employee_count > 100:
        segment = "enterprise"
    elif revenue > 1000000 or employee_count > 20:
        segment = "mid-market"
    else:
        segment = "small-business"
        
    if business_type in ["healthcare", "technology"]:
        segment += "-specialized"
        
    return segment


def get_key_factors(features: Dict[str, Any], score: float) -> List[Dict[str, Any]]:
    """Get key factors influencing the lead score."""
    factors = []
    
    # Revenue impact
    revenue = features.get("annual_revenue", 0)
    if revenue > 5000000:
        factors.append({
            "factor": "High Annual Revenue",
            "impact": "positive",
            "description": "Business with >$5M revenue has higher conversion probability",
            "weight": 0.15
        })
    elif revenue < 500000:
        factors.append({
            "factor": "Low Annual Revenue",
            "impact": "negative",
            "description": "Business with <$500K revenue has lower conversion probability",
            "weight": -0.05
        })
    
    # Engagement impact
    if features.get("quote_form_completed", False):
        factors.append({
            "factor": "Completed Quote Form",
            "impact": "positive",
            "description": "Lead has completed the quote form, showing high intent",
            "weight": 0.2
        })
    
    # Industry impact
    business_type = features.get("business_type", "").lower()
    if business_type in ["technology", "healthcare", "professional_services"]:
        factors.append({
            "factor": f"{business_type.title()} Industry",
            "impact": "positive",
            "description": f"{business_type.title()} businesses show higher conversion rates",
            "weight": 0.1
        })
    elif business_type in ["retail"]:
        factors.append({
            "factor": "Retail Industry",
            "impact": "neutral",
            "description": "Retail businesses show average conversion rates",
            "weight": 0.0
        })
    
    # Previous relationship
    if features.get("previous_insurance", False):
        factors.append({
            "factor": "Previous Insurance Customer",
            "impact": "positive",
            "description": "Lead has purchased insurance before, showing familiarity",
            "weight": 0.05
        })
        
    return factors


def get_recommended_actions(features: Dict[str, Any], score: float, priority: str) -> List[str]:
    """Get recommended actions based on features and score."""
    actions = []
    
    if priority == "high":
        actions.append("Assign to senior agent for immediate follow-up")
        actions.append("Prepare personalized quote options")
        
        if features.get("business_type", "").lower() in ["technology", "healthcare"]:
            actions.append("Include specialized coverage options for industry-specific risks")
    
    elif priority == "medium":
        actions.append("Schedule follow-up call within 48 hours")
        actions.append("Send information packet about relevant coverage options")
        
        if not features.get("quote_form_completed", False):
            actions.append("Send reminder to complete quote form")
    
    else:  # low priority
        actions.append("Add to nurture email campaign")
        actions.append("Schedule follow-up in 1-2 weeks")
    
    return actions


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "lead-scoring"}


@app.post("/score", response_model=LeadScore)
async def score_lead(lead: LeadFeatures):
    """Score a single lead."""
    try:
        # Generate a unique ID
        lead_id = f"lead_{int(datetime.now().timestamp() * 1000)}"
        
        # Convert lead features to dictionary
        features = lead.dict()
        
        # Make predictions
        start_time = datetime.now()
        
        conversion_prob = predict_conversion_probability(features)
        estimated_premium = predict_premium_value(features)
        priority = determine_priority(conversion_prob)
        segment = determine_segment(features)
        key_factors = get_key_factors(features, conversion_prob)
        recommended_actions = get_recommended_actions(features, conversion_prob, priority)
        
        # Calculate estimated close time (would be a real ML model)
        if conversion_prob > 0.7:
            estimated_close_time = 14  # 2 weeks
        elif conversion_prob > 0.4:
            estimated_close_time = 30  # 1 month
        else:
            estimated_close_time = 60  # 2 months
        
        # Prepare response
        score_response = LeadScore(
            lead_id=lead_id,
            score=conversion_prob,
            conversion_probability=conversion_prob,
            priority=priority,
            estimated_premium=estimated_premium,
            estimated_close_time_days=estimated_close_time,
            key_factors=key_factors,
            segment=segment,
            recommended_actions=recommended_actions,
            scored_at=datetime.now().isoformat()
        )
        
        # Log the scoring
        logger.info(f"Scored lead: {lead_id}, score: {conversion_prob:.2f}, priority: {priority}")
        
        return score_response
    
    except Exception as e:
        logger.error(f"Error scoring lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scoring lead: {str(e)}")


@app.post("/batch-score", response_model=LeadScoringResponse)
async def batch_score_leads(request: LeadScoringRequest):
    """Score multiple leads in a batch."""
    try:
        start_time = datetime.now()
        
        results = []
        for lead_data in request.leads:
            # Convert to LeadFeatures model for validation
            lead = LeadFeatures(**lead_data)
            
            # Generate a unique ID
            lead_id = f"lead_{int(datetime.now().timestamp() * 1000)}"
            
            # Make predictions
            features = lead.dict()
            conversion_prob = predict_conversion_probability(features)
            estimated_premium = predict_premium_value(features)
            priority = determine_priority(conversion_prob)
            segment = determine_segment(features)
            
            # Only include explanations if requested
            if request.include_explanations:
                key_factors = get_key_factors(features, conversion_prob)
                recommended_actions = get_recommended_actions(features, conversion_prob, priority)
            else:
                key_factors = []
                recommended_actions = []
            
            # Calculate estimated close time
            if conversion_prob > 0.7:
                estimated_close_time = 14  # 2 weeks
            elif conversion_prob > 0.4:
                estimated_close_time = 30  # 1 month
            else:
                estimated_close_time = 60  # 2 months
            
            # Prepare result
            score_result = LeadScore(
                lead_id=lead_id,
                score=conversion_prob,
                conversion_probability=conversion_prob,
                priority=priority,
                estimated_premium=estimated_premium,
                estimated_close_time_days=estimated_close_time,
                key_factors=key_factors,
                segment=segment,
                recommended_actions=recommended_actions,
                scored_at=datetime.now().isoformat()
            )
            
            results.append(score_result)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log the batch scoring
        logger.info(f"Batch scored {len(results)} leads in {processing_time_ms:.2f}ms")
        
        return LeadScoringResponse(
            results=results,
            processing_time_ms=processing_time_ms
        )
    
    except Exception as e:
        logger.error(f"Error batch scoring leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error batch scoring leads: {str(e)}")


@app.get("/analytics/conversion-factors")
async def get_conversion_factors():
    """Get key factors affecting conversion probability."""
    # This would typically come from model analysis in production
    return {
        "business_type_factors": {
            "technology": 0.15,
            "healthcare": 0.12,
            "professional_services": 0.13,
            "retail": 0.10,
            "manufacturing": 0.05,
            "construction": 0.08
        },
        "revenue_factors": {
            "over_5M": 0.15,
            "1M_to_5M": 0.10,
            "500K_to_1M": 0.05,
            "under_500K": 0.00
        },
        "engagement_factors": {
            "quote_form_completed": 0.20,
            "quote_form_started": 0.10,
            "extended_website_visit": 0.05
        },
        "relationship_factors": {
            "previous_insurance": 0.05,
            "previous_contact": 0.03
        }
    }


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3005"))
    reload = os.getenv("RELOAD", "True").lower() in ("true", "1", "t")
    
    # Start the API server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
