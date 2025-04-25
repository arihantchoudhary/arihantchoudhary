import os
import logging
import json
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union
import httpx

from .config import settings

# Setup logging
logger = logging.getLogger("document-parser.parsers")


class DocumentParser(ABC):
    """Abstract base class for document parsers."""
    
    @abstractmethod
    async def parse(self, file_path: str, fields_of_interest: Optional[List[str]] = None) -> Dict[str, Tuple[Any, float]]:
        """
        Parse a document and extract structured information.
        
        Args:
            file_path: Path to the document file
            fields_of_interest: Optional list of specific fields to extract
            
        Returns:
            A dictionary mapping field names to tuples of (value, confidence)
        """
        pass


class LlamaDocumentParser(DocumentParser):
    """Document parser that uses LlamaParser API."""
    
    def __init__(self):
        self.api_key = settings.LLAMA_PARSER_API_KEY
        self.api_url = settings.LLAMA_PARSER_API_URL
        self.timeout = settings.LLAMA_PARSER_TIMEOUT
        
        if not self.api_key:
            logger.warning("No LlamaParser API key provided. Using mock parser.")
    
    async def parse(self, file_path: str, fields_of_interest: Optional[List[str]] = None) -> Dict[str, Tuple[Any, float]]:
        """Parse document using LlamaParser API."""
        try:
            # If no API key is provided, return mock results for development
            if not self.api_key:
                return await self._mock_parse(file_path, fields_of_interest)
            
            # Get file extension
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower().replace(".", "")
            
            # Read file
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/octet-stream"
            }
            
            params = {
                "file_type": file_extension,
                "extraction_level": "detailed"
            }
            
            if fields_of_interest:
                params["fields"] = ",".join(fields_of_interest)
            
            # Send request to LlamaParser API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/v1/parse",
                    headers=headers,
                    params=params,
                    content=file_data
                )
                
                if response.status_code != 200:
                    logger.error(f"LlamaParser API error: {response.status_code} - {response.text}")
                    return await self._mock_parse(file_path, fields_of_interest)
                
                # Process response
                result = response.json()
                
                # Convert to expected format
                parsed_data = {}
                for field, field_data in result.get("fields", {}).items():
                    parsed_data[field] = (field_data.get("value"), field_data.get("confidence", 0.8))
                
                # Add document type and summary
                parsed_data["document_type"] = result.get("document_type", "unknown")
                parsed_data["summary"] = result.get("summary", "")
                
                return parsed_data
                
        except Exception as e:
            logger.error(f"Error parsing document: {str(e)}")
            return await self._mock_parse(file_path, fields_of_interest)
    
    async def _mock_parse(self, file_path: str, fields_of_interest: Optional[List[str]] = None) -> Dict[str, Tuple[Any, float]]:
        """Return mock parsing results for development."""
        # Get filename without extension
        filename = os.path.basename(file_path)
        
        # Determine document type based on filename
        document_type = "unknown"
        if "application" in filename.lower():
            document_type = "insurance_application"
            mock_data = self._mock_application_data()
        elif "policy" in filename.lower():
            document_type = "insurance_policy"
            mock_data = self._mock_policy_data()
        elif "claim" in filename.lower():
            document_type = "insurance_claim"
            mock_data = self._mock_claim_data()
        else:
            mock_data = self._mock_general_data()
        
        # Add document type and summary
        mock_data["document_type"] = (document_type, 0.9)
        mock_data["summary"] = (f"This appears to be a {document_type.replace('_', ' ')} document.", 0.85)
        
        # Filter fields if requested
        if fields_of_interest:
            filtered_data = {
                k: v for k, v in mock_data.items() 
                if k in fields_of_interest or k in ["document_type", "summary"]
            }
            return filtered_data
        
        return mock_data
    
    def _mock_application_data(self) -> Dict[str, Tuple[Any, float]]:
        """Return mock data for an insurance application."""
        return {
            "applicant_name": ("John Smith", 0.95),
            "business_name": ("Acme Retail Solutions", 0.92),
            "business_type": ("Retail", 0.88),
            "address": ("123 Main St, San Francisco, CA 94105", 0.9),
            "phone": ("415-555-1234", 0.95),
            "email": ("john@acmeretail.com", 0.92),
            "tax_id": ("12-3456789", 0.85),
            "annual_revenue": ("$1,200,000", 0.8),
            "employee_count": (12, 0.9),
            "industry": ("Retail", 0.85),
            "coverage_types": (["General Liability", "Property", "Workers Compensation"], 0.87),
            "existing_policies": ([], 0.6)
        }
    
    def _mock_policy_data(self) -> Dict[str, Tuple[Any, float]]:
        """Return mock data for an insurance policy."""
        return {
            "policy_number": ("POL-123456789", 0.97),
            "carrier": ("Insurance Company A", 0.94),
            "policy_type": ("Commercial General Liability", 0.92),
            "effective_date": ("2024-01-01", 0.9),
            "expiration_date": ("2025-01-01", 0.9),
            "premium": (3500.00, 0.85),
            "coverage_limits": ({"per_occurrence": "$1,000,000", "aggregate": "$2,000,000"}, 0.82),
            "deductibles": ({"general": "$500"}, 0.8)
        }
    
    def _mock_claim_data(self) -> Dict[str, Tuple[Any, float]]:
        """Return mock data for an insurance claim."""
        return {
            "claim_number": ("CLM-20230415-001", 0.96),
            "policy_number": ("POL-123456789", 0.94),
            "claimant_name": ("John Smith", 0.92),
            "incident_date": ("2023-04-15", 0.9),
            "filing_date": ("2023-04-17", 0.9),
            "incident_description": ("Water damage from broken pipe in office kitchen", 0.85),
            "claim_amount": (12500.00, 0.82),
            "claim_status": ("Under Review", 0.9),
            "adjuster": ("Jane Doe", 0.85)
        }
    
    def _mock_general_data(self) -> Dict[str, Tuple[Any, float]]:
        """Return general mock data for an unidentified document."""
        return {
            "business_name": ("Acme Corporation", 0.85),
            "document_date": ("2023-09-15", 0.8),
            "reference_number": ("REF-2023091501", 0.75),
            "document_title": ("Business Document", 0.7),
            "contact_info": ("415-555-1234, info@acmecorp.com", 0.8)
        }


class PDFDocumentParser(DocumentParser):
    """Parser specifically optimized for PDF documents."""
    
    def __init__(self):
        self.llama_parser = LlamaDocumentParser()
    
    async def parse(self, file_path: str, fields_of_interest: Optional[List[str]] = None) -> Dict[str, Tuple[Any, float]]:
        """Parse PDF document."""
        # For now, delegate to LlamaParser
        # In a real implementation, this could have PDF-specific pre-processing
        return await self.llama_parser.parse(file_path, fields_of_interest)


class DocxDocumentParser(DocumentParser):
    """Parser specifically optimized for DOCX documents."""
    
    def __init__(self):
        self.llama_parser = LlamaDocumentParser()
    
    async def parse(self, file_path: str, fields_of_interest: Optional[List[str]] = None) -> Dict[str, Tuple[Any, float]]:
        """Parse DOCX document."""
        # For now, delegate to LlamaParser
        # In a real implementation, this could have DOCX-specific pre-processing
        return await self.llama_parser.parse(file_path, fields_of_interest)


class ImageDocumentParser(DocumentParser):
    """Parser specifically optimized for image documents (JPG, PNG)."""
    
    def __init__(self):
        self.llama_parser = LlamaDocumentParser()
    
    async def parse(self, file_path: str, fields_of_interest: Optional[List[str]] = None) -> Dict[str, Tuple[Any, float]]:
        """Parse image document."""
        # For now, delegate to LlamaParser
        # In a real implementation, this could have image-specific pre-processing
        return await self.llama_parser.parse(file_path, fields_of_interest)


class DocumentParserFactory:
    """Factory for creating appropriate document parsers."""
    
    @staticmethod
    def get_parser(file_type: str) -> DocumentParser:
        """
        Get appropriate parser for file type.
        
        Args:
            file_type: File extension without dot (e.g., 'pdf', 'docx')
            
        Returns:
            A DocumentParser instance appropriate for the file type
        """
        file_type = file_type.lower()
        
        if file_type in ["pdf"]:
            return PDFDocumentParser()
        elif file_type in ["docx", "doc"]:
            return DocxDocumentParser()
        elif file_type in ["jpg", "jpeg", "png"]:
            return ImageDocumentParser()
        else:
            # Default to LlamaParser for unknown file types
            return LlamaDocumentParser()
