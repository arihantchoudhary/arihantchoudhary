import os
import logging
import json
import time
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("document-parser")

# Create FastAPI app
app = FastAPI(
    title="Harper Document Parser",
    description="Document parsing service for insurance forms and applications",
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

# Import other modules after app initialization to avoid circular imports
from .config import settings
from .models import (
    DocumentUploadResponse,
    DocumentParseResponse,
    DocumentMetadata,
    FieldExtraction,
    ParseRequest
)
from .parsers import LlamaDocumentParser, DocumentParserFactory

# Create temp directory if it doesn't exist
os.makedirs(settings.STORAGE_PATH, exist_ok=True)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "document-parser"}

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    auto_parse: bool = Query(False, description="Automatically parse document after upload")
):
    """
    Upload a document for parsing.
    
    - Supports PDF, DOCX, JPG, PNG formats
    - Returns a document ID that can be used to retrieve parsing results
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension}. Supported formats: {settings.SUPPORTED_FORMATS}"
            )
        
        # Generate a unique document ID
        document_id = f"doc_{int(time.time() * 1000)}"
        
        # Save file to temporary storage
        file_path = os.path.join(settings.STORAGE_PATH, f"{document_id}{file_extension}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Document uploaded: {file.filename} (ID: {document_id})")
        
        # Create document metadata
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=file.filename,
            file_type=file_extension.replace(".", ""),
            file_size=os.path.getsize(file_path),
            upload_timestamp=datetime.datetime.now().isoformat(),
            status="uploaded"
        )
        
        # Store metadata
        # In a real implementation, this would be saved to a database
        metadata_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_metadata.json")
        with open(metadata_path, "w") as f:
            f.write(metadata.model_dump_json())
        
        # Schedule background parsing if requested
        if auto_parse and background_tasks:
            background_tasks.add_task(
                parse_document_task,
                document_id=document_id,
                file_path=file_path,
                file_type=file_extension.replace(".", "")
            )
            parse_status = "processing"
        else:
            parse_status = "pending"
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_type=file_extension.replace(".", ""),
            file_size=os.path.getsize(file_path),
            parse_status=parse_status,
            message="Document uploaded successfully"
        )
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.post("/parse/{document_id}", response_model=DocumentParseResponse)
async def parse_document(document_id: str, request: Optional[ParseRequest] = None):
    """
    Parse a previously uploaded document.
    
    - Extracts structured data from the document using LlamaParser
    - Can specify fields of interest in the request body
    """
    try:
        # Check if document exists
        metadata_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_metadata.json")
        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
        
        # Load metadata
        with open(metadata_path, "r") as f:
            metadata = DocumentMetadata.model_validate_json(f.read())
        
        # Find the document file
        file_path = os.path.join(settings.STORAGE_PATH, f"{document_id}.{metadata.file_type}")
        if not os.path.exists(file_path):
            file_path = os.path.join(settings.STORAGE_PATH, f"{document_id}{metadata.file_type}")
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"Document file not found: {document_id}")
        
        # Get appropriate parser
        parser = DocumentParserFactory.get_parser(metadata.file_type)
        
        # Parse document
        fields_of_interest = request.fields if request and request.fields else None
        parse_results = await parser.parse(file_path, fields_of_interest)
        
        # Update metadata
        metadata.status = "parsed"
        metadata.parsed_timestamp = datetime.datetime.now().isoformat()
        with open(metadata_path, "w") as f:
            f.write(metadata.model_dump_json())
        
        # Save parsing results
        results_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_results.json")
        with open(results_path, "w") as f:
            f.write(json.dumps(parse_results))
        
        return DocumentParseResponse(
            document_id=document_id,
            status="success",
            extracted_fields=[
                FieldExtraction(
                    field_name=field,
                    value=value,
                    confidence=confidence
                )
                for field, (value, confidence) in parse_results.items()
            ],
            document_type=parse_results.get("document_type", "unknown"),
            summary=parse_results.get("summary", ""),
            message="Document parsed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing document: {str(e)}")

@app.get("/documents/{document_id}", response_model=DocumentMetadata)
async def get_document_metadata(document_id: str):
    """Get metadata for a specific document."""
    try:
        metadata_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_metadata.json")
        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
        
        with open(metadata_path, "r") as f:
            metadata = DocumentMetadata.model_validate_json(f.read())
        
        return metadata
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document metadata: {str(e)}")

@app.get("/documents/{document_id}/results", response_model=DocumentParseResponse)
async def get_parse_results(document_id: str):
    """Get parsing results for a specific document."""
    try:
        results_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_results.json")
        if not os.path.exists(results_path):
            raise HTTPException(status_code=404, detail="Parsing results not found")
        
        with open(results_path, "r") as f:
            parse_results = json.loads(f.read())
        
        return DocumentParseResponse(
            document_id=document_id,
            status="success",
            extracted_fields=[
                FieldExtraction(
                    field_name=field,
                    value=value,
                    confidence=confidence
                )
                for field, (value, confidence) in parse_results.items()
                if field not in ["document_type", "summary"]
            ],
            document_type=parse_results.get("document_type", "unknown"),
            summary=parse_results.get("summary", ""),
            message="Retrieved parsing results"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving parsing results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving parsing results: {str(e)}")

async def parse_document_task(document_id: str, file_path: str, file_type: str):
    """Background task for document parsing."""
    try:
        # Get appropriate parser
        parser = DocumentParserFactory.get_parser(file_type)
        
        # Parse document
        parse_results = await parser.parse(file_path)
        
        # Update metadata
        metadata_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_metadata.json")
        with open(metadata_path, "r") as f:
            metadata = DocumentMetadata.model_validate_json(f.read())
        
        metadata.status = "parsed"
        metadata.parsed_timestamp = datetime.datetime.now().isoformat()
        
        with open(metadata_path, "w") as f:
            f.write(metadata.model_dump_json())
        
        # Save parsing results
        results_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_results.json")
        with open(results_path, "w") as f:
            f.write(json.dumps(parse_results))
        
        logger.info(f"Document parsed successfully: {document_id}")
    
    except Exception as e:
        logger.error(f"Error in background parsing task: {str(e)}")
        # Update metadata to indicate failure
        try:
            metadata_path = os.path.join(settings.STORAGE_PATH, f"{document_id}_metadata.json")
            with open(metadata_path, "r") as f:
                metadata = DocumentMetadata.model_validate_json(f.read())
            
            metadata.status = "failed"
            metadata.error = str(e)
            
            with open(metadata_path, "w") as f:
                f.write(metadata.model_dump_json())
        except Exception:
            pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
