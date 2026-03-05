from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, UniqueConstraint, Enum, CheckConstraint, PrimaryKeyConstraint, ARRAY
from app.db import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import FetchedValue
from datetime import datetime, UTC
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import (
	Column,
	String,
	Boolean,
	Text,
	ForeignKey,
	Enum,
	DateTime,
	PrimaryKeyConstraint,
	Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import enum

from app.db import Base

class User(Base):
	"""
	SQLAlchemy model for the 'users' table.
	"""
	__tablename__ = "users"

	user_id = Column(String, primary_key=True, index=True, server_default=FetchedValue())
	username = Column(String, unique=True, index=True)
	email = Column(String)
	hash_password = Column(String)

	def __repr__(self):
		return f"<User(user_id='{self.user_id}', username='{self.username}', , email='{self.email}')>"



class AgentServicePermission(str, enum.Enum):
	admin = "admin"
	member = "member"
	observer = "observer"


class Agent(Base):
	"""
	SQLAlchemy model for the 'agents' table.
	"""
	__tablename__ = "agents"

	agent_id = Column(String, primary_key=True, index=True, server_default=FetchedValue())
	user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

	name = Column(String, nullable=False)
	is_active = Column(Boolean, nullable=False, default=True, server_default=FetchedValue())

	# Relationships
	user = relationship("User", backref="agents")
	services = relationship("AgentService", back_populates="agent", cascade="all, delete-orphan")
	logs = relationship("Log", back_populates="agent", cascade="all, delete-orphan")

	def __repr__(self):
		return f"<Agent(agent_id='{self.agent_id}', user_id='{self.user_id}', name='{self.name}', is_active={self.is_active})>"


class Service(Base):
	"""
	SQLAlchemy model for the 'services' table.
	"""
	__tablename__ = "services"

	service_id = Column(String, primary_key=True, index=True, server_default=FetchedValue())
	name = Column(String, nullable=False, unique=True, index=True)

	manifest = Column(JSONB, nullable=False)

	# Relationships
	agents = relationship("AgentService", back_populates="service", cascade="all, delete-orphan")
	logs = relationship("Log", back_populates="service", cascade="all, delete-orphan")

	def __repr__(self):
		return f"<Service(service_id='{self.service_id}', name='{self.name}')>"


class AgentService(Base):
	"""
	Join table between agents and services.
	"""
	__tablename__ = "agent_service"

	agent_id = Column(String, ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False)
	service_id = Column(String, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)

	permission = Column(
		Enum(AgentServicePermission, name="agent_service_permission"),
		nullable=False,
		default=AgentServicePermission.member,
		server_default=FetchedValue(),
	)

	__table_args__ = (
		PrimaryKeyConstraint("agent_id", "service_id", name="pk_agent_service"),
		Index("idx_agent_service_service_id", "service_id"),
		Index("idx_agent_service_permission", "permission"),
	)

	# Relationships
	agent = relationship("Agent", back_populates="services")
	service = relationship("Service", back_populates="agents")

	def __repr__(self):
		return f"<AgentService(agent_id='{self.agent_id}', service_id='{self.service_id}', permission='{self.permission.value}')>"


class Log(Base):
	"""
	SQLAlchemy model for the 'logs' table.
	"""
	__tablename__ = "logs"

	log_id = Column(String, primary_key=True, index=True, server_default=FetchedValue())

	agent_id = Column(String, ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False, index=True)
	service_id = Column(String, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False, index=True)

	endpoint = Column(Text, nullable=False)
	log_timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), server_default=FetchedValue())
	is_success = Column(Boolean, nullable=False)
	message = Column(Text, nullable=True)

	__table_args__ = (
		Index("idx_logs_timestamp", "log_timestamp"),
		Index("idx_logs_agent_service_time", "agent_id", "service_id", "log_timestamp"),
	)

	# Relationships
	agent = relationship("Agent", back_populates="logs")
	service = relationship("Service", back_populates="logs")

	def __repr__(self):
		return (
			f"<Log(log_id='{self.log_id}', agent_id='{self.agent_id}', service_id='{self.service_id}', "
			f"endpoint='{self.endpoint}', is_success={self.is_success}, log_timestamp='{self.log_timestamp}')>"
		)

# ==========================================================
# JUST FOR TEST PURPOSE
# TODO do a proper validation function at load to test mapping consistency
# ==========================================================

from sqlalchemy import inspect, Table, MetaData
from sqlalchemy.orm import class_mapper
from app.db import engine

metadata = MetaData()
metadata.reflect(engine, only=["users"])

db_table = metadata.tables["users"]

model_mapper = class_mapper(User)
model_table = model_mapper.local_table

# Check columns
print("DB columns:", db_table.columns.keys())
print("Model columns:", model_table.columns.keys())

# Check primary keys
print("DB primary key:", [col.name for col in db_table.primary_key])
print("Model primary key:", [col.name for col in model_table.primary_key])
