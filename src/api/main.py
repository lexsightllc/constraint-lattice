# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 ochoaughini. See LICENSE for full terms.
# Copyright (c) 2025 Lexsight LCC. All rights reserved.
# See saas/LICENSE-BSL.txt for full terms.
# Copyright (c) 2025 Lexsight LCC. All rights reserved.
# See saas/LICENSE-BSL.txt for full terms.
import json
import logging
from typing import Any, Dict, List, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# Local imports
from constraint_lattice.engine.apply import apply_constraints, AuditStep
from constraint_lattice.constraints.profanity import ProfanityFilter
from constraint_lattice.constraints.length import LengthConstraint
from .ws import manager

# Initialize FastAPI app
app = FastAPI(
    title="Constraint Lattice API",
    description="Deterministic, auditable post-processing governance framework for LLM outputs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConstraintRequest(BaseModel):
    """Request model for constraint application.

    Attributes:
        text: Text to process (max 100,000 characters)
        constraints: List of constraint configurations (max 50 constraints)
    """
    text: str = Field(..., min_length=1, max_length=100_000, description="Text to process")
    constraints: List[Dict[str, Any]] = Field(..., min_length=1, max_length=50, description="Constraint configurations")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text input is not empty after stripping."""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate constraint configurations."""
        for constraint in v:
            if "type" not in constraint:
                raise ValueError("Each constraint must have a 'type' field")
        return v


class ConstraintResponse(BaseModel):
    """Response model for constraint application.

    Attributes:
        result: Text after constraint application
        steps: Optional audit trace of applied constraints
        metadata: Optional metadata about the processing
    """
    result: str = Field(..., description="Processed text after constraint application")
    steps: Optional[List[Dict[str, Any]]] = Field(None, description="Audit trace of applied constraints")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Processing metadata")


@app.post("/api/constraints/apply", response_model=ConstraintResponse, status_code=status.HTTP_200_OK)
async def apply_constraints_endpoint(request: ConstraintRequest) -> Dict[str, Any]:
    """Apply constraints to input text.

    This endpoint applies a series of constraints to the provided text and returns
    the processed result along with an optional audit trace for governance and compliance.

    Args:
        request: Constraint application request containing text and constraint configurations

    Returns:
        Dictionary containing:
        - result: Processed text after constraint application
        - steps: Optional audit trace of each constraint application
        - metadata: Processing information (constraint count, execution time, etc.)

    Raises:
        HTTPException:
            - 400: Invalid constraint configuration or missing required parameters
            - 422: Validation error in request
            - 500: Internal server error during constraint processing
    """
    import time
    start_time = time.time()

    try:
        constraint_objs = []
        unknown_types = []

        for idx, constraint_config in enumerate(request.constraints):
            constraint_type = constraint_config.get("type")

            if constraint_type == "profanity":
                constraint_objs.append(ProfanityFilter(
                    replacement=constraint_config.get("replacement", "[FILTERED]")
                ))
            elif constraint_type == "length":
                if "max" not in constraint_config:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Length constraint at index {idx} missing required 'max' parameter"
                    )
                constraint_objs.append(LengthConstraint(
                    max_length=constraint_config["max"],
                    truncate=constraint_config.get("truncate", True),
                    ellipsis=constraint_config.get("ellipsis", "[...]")
                ))
            else:
                unknown_types.append(constraint_type)
                logger.warning(f"Unknown constraint type at index {idx}: {constraint_type}")

        if unknown_types and not constraint_objs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No valid constraints found. Unknown types: {', '.join(unknown_types)}"
            )

        # Log the constraint objects
        logger.info(f"Processing request with {len(constraint_objs)} valid constraints")
        for i, obj in enumerate(constraint_objs):
            logger.debug(f"Constraint {i}: {obj.__class__.__name__}")

        # Apply constraints
        processed, trace = apply_constraints(
            prompt="",
            output=request.text,
            constraints=constraint_objs,
            return_trace=True
        )

        # Broadcast trace updates to WebSocket clients
        try:
            for step in trace:
                await manager.broadcast(json.dumps(step.to_dict()))
        except Exception as ws_error:
            logger.warning(f"Failed to broadcast to WebSocket clients: {ws_error}")

        # Convert audit trace to serializable format
        audit_trace = [step.to_dict() for step in trace] if trace else None

        # Calculate processing metadata
        execution_time = time.time() - start_time
        metadata = {
            "execution_time_seconds": round(execution_time, 4),
            "constraints_applied": len(constraint_objs),
            "unknown_constraint_types": unknown_types if unknown_types else None,
            "original_length": len(request.text),
            "processed_length": len(processed),
        }

        return {
            "result": processed,
            "steps": audit_trace,
            "metadata": metadata
        }

    except HTTPException:
        raise
    except KeyError as e:
        logger.error(f"Missing required parameter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required parameter: {e}"
        )
    except ValueError as e:
        logger.error(f"Invalid value: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid value: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error applying constraints")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Status message
    """
    return {"status": "healthy"}


@app.websocket("/ws/trace")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time constraint application.
    
    Args:
        websocket: WebSocket connection
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
