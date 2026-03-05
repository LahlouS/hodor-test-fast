# app/routers/logic.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any

from app.models import Agent, Service, AgentService, Log, AgentServicePermission  # adjust import path
from app.db.dependencies import db_dependency
from app.auth.dependencies import user_dependency

router = APIRouter(
    prefix="/logic",
    tags=["logic"],
)

# -------------------------
# Pydantic schemas (simple)
# -------------------------

class AgentCreateIn(BaseModel):
    name: str
    is_active: bool = True


class AgentOut(BaseModel):
    agent_id: str
    user_id: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True

    @field_validator('agent_id', 'user_id', mode='before')
    @classmethod
    def _uuid_to_str(cls, v): return str(v) if v is not None else v


class AgentServiceAddIn(BaseModel):
    agent_id: str
    service_id: str
    permission: AgentServicePermission = AgentServicePermission.member


class ServiceOut(BaseModel):
    service_id: str
    name: str
    manifest: Any

    class Config:
        from_attributes = True

    @field_validator('service_id', mode='before')
    @classmethod
    def _uuid_to_str(cls, v): return str(v) if v is not None else v


class AgentServiceOut(BaseModel):
    agent_id: str
    service_id: str
    permission: AgentServicePermission

    class Config:
        from_attributes = True

    @field_validator('agent_id', 'service_id', mode='before')
    @classmethod
    def _uuid_to_str(cls, v): return str(v) if v is not None else v


class LogOut(BaseModel):
    log_id: str
    agent_id: str
    service_id: str
    endpoint: str
    log_timestamp: Any
    is_success: bool
    message: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator('log_id', 'agent_id', 'service_id', mode='before')
    @classmethod
    def _uuid_to_str(cls, v): return str(v) if v is not None else v


# -------------------------
# Helpers
# -------------------------

def _require_user(user):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification failed",
        )


# -------------------------
# Routes
# -------------------------

@router.post("/agents", status_code=status.HTTP_201_CREATED, response_model=AgentOut)
async def create_agent(payload: AgentCreateIn, user: "user_dependency", db: "db_dependency"):
    """
    Create a new agent for the authenticated user.
    Default is_active = true (can be overridden by payload).
    """
    _require_user(user)

    agent = Agent(
        user_id=user["id"],
        name=payload.name,
        is_active=payload.is_active,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.post("/agents/services", status_code=status.HTTP_201_CREATED, response_model=AgentServiceOut)
async def add_service_to_agent(payload: AgentServiceAddIn, user: "user_dependency", db: "db_dependency"):
    """
    Attach a service to an agent with a permission level.
    """
    _require_user(user)

    agent = db.query(Agent).filter(Agent.agent_id == payload.agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    # Ownership check: user can only manage their own agents
    if agent.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    service = db.query(Service).filter(Service.service_id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    existing = (
        db.query(AgentService)
        .filter(
            AgentService.agent_id == payload.agent_id,
            AgentService.service_id == payload.service_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service already attached to this agent")

    link = AgentService(
        agent_id=payload.agent_id,
        service_id=payload.service_id,
        permission=payload.permission,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.get("/services", status_code=status.HTTP_200_OK, response_model=List[ServiceOut])
async def list_services(user: "user_dependency", db: "db_dependency"):
    """
    List all available services (with all infos).
    """
    _require_user(user)

    services = db.query(Service).order_by(Service.name.asc()).all()
    return services


@router.get("/agents/{agent_id}/logs", status_code=status.HTTP_200_OK, response_model=List[LogOut])
async def get_agent_logs(agent_id: str, user: "user_dependency", db: "db_dependency"):
    """
    Get logs for a given agent_id (only if it belongs to the authenticated user).
    """
    _require_user(user)

    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if agent.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    logs = (
        db.query(Log)
        .filter(Log.agent_id == agent_id)
        .order_by(Log.log_timestamp.desc())
        .all()
    )
    return logs


@router.get("/agents", status_code=status.HTTP_200_OK, response_model=List[AgentOut])
async def list_my_agents(user: "user_dependency", db: "db_dependency"):
    """
    Get all agents for the authenticated user.
    """
    _require_user(user)

    agents = (
        db.query(Agent)
        .filter(Agent.user_id == user["id"])
        .order_by(Agent.name.asc())
        .all()
    )
    return agents


@router.get("/agents/{agent_id}/services", status_code=status.HTTP_200_OK, response_model=List[ServiceOut])
async def list_services_for_agent(agent_id: str, user: "user_dependency", db: "db_dependency"):
    """
    Get all services attached to an agent (only if agent belongs to user).
    Returns the full Service objects (all infos).
    """
    _require_user(user)

    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if agent.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    services = (
        db.query(Service)
        .join(AgentService, AgentService.service_id == Service.service_id)
        .filter(AgentService.agent_id == agent_id)
        .order_by(Service.name.asc())
        .all()
    )
    return services