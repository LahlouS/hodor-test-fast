# app/routers/middleware.py

from typing import Annotated, Any, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.models import Agent, Service, AgentService, Log  # adjust import path
from app.db.dependencies import db_dependency
from app.auth.dependencies import user_dependency

router = APIRouter(prefix="/middleware", tags=["middleware"])

# Simple "API token" bearer: user sends `Authorization: Bearer <agent_id>`
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


# -------------------------
# Dependencies
# -------------------------

async def get_agent_token(token: Annotated[str, Depends(oauth2_bearer)]) -> str:
    """
    Super simple: the bearer token IS the agent_id.
    (No JWT validation, just a string.)
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing agent token")
    return token


agent_token_dependency = Annotated[str, Depends(get_agent_token)]


def _find_manifest_route(manifest: Dict[str, Any], endpoint: str) -> Optional[Dict[str, Any]]:
    """
    Manifest example:
    {
      "routes": [
        {"endpoint": "list-repos", "permission": "observer", ...}
      ]
    }
    """
    routes = manifest.get("routes", [])
    for r in routes:
        if r.get("endpoint") == endpoint:
            return r
    return None


async def verify_service_agent_endpoint(
    service_name: str,
    endpoint: str,
    agent_token: agent_token_dependency,
    db: "db_dependency",
) -> dict:
    """
    Verify:
      - service exists by name
      - endpoint exists in service.manifest.routes[*].endpoint
      - agent exists and is active
      - agent is connected to service (agent_service row exists)

    Returns a small context dict for the route handler.
    """
    # 1) Service exists
    service = db.query(Service).filter(Service.name == service_name).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    # 2) Endpoint exists in manifest
    route_def = _find_manifest_route(service.manifest or {}, endpoint)
    if not route_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found in service manifest")

    # 3) Agent exists (token == agent_id)
    agent = db.query(Agent).filter(Agent.agent_id == agent_token).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent token")
    if not agent.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent is not active")

    # 4) Agent has the service connected
    link = (
        db.query(AgentService)
        .filter(AgentService.agent_id == agent.agent_id, AgentService.service_id == service.service_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent has no access to this service")

    return {
        "agent": agent,
        "service": service,
        "route_def": route_def,
        "agent_service": link,
    }


verify_dependency = Annotated[dict, Depends(verify_service_agent_endpoint)]


# -------------------------
# Route
# -------------------------

@router.api_route("/{service_name}/{endpoint}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def middleware_entrypoint(
    request: Request,
    service_name: str,
    endpoint: str,
    ctx: verify_dependency,
    db: "db_dependency",
):
    """
    Super simple middleware "proxy" endpoint:
    - verifies service/endpoint/agent access via dependency
    - logs success/failure
    - returns {"success": true/false}

    (No real forwarding to GitHub/Slack yet.)
    """
    agent: Agent = ctx["agent"]
    service: Service = ctx["service"]

    # If we reached here, verification succeeded.
    is_success = True
    message = "OK"

    try:
        # Here is where you'd forward to the real upstream later.
        # For now: do nothing and return success.
        pass
    except Exception as e:
        is_success = False
        message = f"Error: {type(e).__name__}"

    # Log (super simple)
    log = Log(
        agent_id=agent.agent_id,
        service_id=service.service_id,
        endpoint=endpoint,
        log_timestamp=datetime.now(UTC),
        is_success=is_success,
        message=message,
    )
    db.add(log)
    db.commit()

    return {"success": is_success}