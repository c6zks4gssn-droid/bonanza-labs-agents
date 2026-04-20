"""Core agent models — Agent, Task, Tool, Workflow."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    ERROR = "error"
    STOPPED = "stopped"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolType(str, Enum):
    SEARCH = "search"
    VIDEO = "video"
    WALLET = "wallet"
    WEBHOOK = "webhook"
    CODE = "code"
    HTTP = "http"
    CUSTOM = "custom"


class Tool(BaseModel):
    """A tool an agent can use."""
    name: str
    type: ToolType
    description: str = ""
    config: dict = {}
    enabled: bool = True


class Agent(BaseModel):
    """An AI agent with tools, memory, and payment capabilities."""
    id: str = Field(default_factory=lambda: f"agent_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    name: str
    description: str = ""
    model: str = "glm-5.1:cloud"
    provider: str = "ollama"
    system_prompt: str = "You are a helpful AI agent."
    tools: list[Tool] = []
    status: AgentStatus = AgentStatus.IDLE
    wallet_id: str = ""  # Links to Agent Wallet
    budget_limit_usd: float = 10.0
    max_turns: int = 20
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = {}


class Task(BaseModel):
    """A task assigned to an agent."""
    id: str = Field(default_factory=lambda: f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    agent_id: str
    prompt: str
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    tools_used: list[str] = []
    started_at: str = ""
    completed_at: str = ""
    metadata: dict = {}


class WorkflowStep(BaseModel):
    """A step in a workflow."""
    agent_id: str
    prompt: str
    tool: str = ""
    condition: str = ""  # Python expression to evaluate
    on_success: str = ""  # Next step ID
    on_failure: str = ""  # Next step ID or "stop"


class Workflow(BaseModel):
    """A multi-agent workflow."""
    id: str = Field(default_factory=lambda: f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    name: str
    description: str = ""
    steps: list[WorkflowStep] = []
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# ─── Built-in tool definitions ───

BUILT_IN_TOOLS = {
    "search": Tool(name="search", type=ToolType.SEARCH, description="Web search and extract"),
    "video": Tool(name="video", type=ToolType.VIDEO, description="Generate video with FrameForge"),
    "wallet": Tool(name="wallet", type=ToolType.WALLET, description="Send payments via Agent Wallet"),
    "webhook": Tool(name="webhook", type=ToolType.WEBHOOK, description="Send/receive webhooks"),
    "code": Tool(name="code", type=ToolType.CODE, description="Execute code in sandbox"),
    "http": Tool(name="http", type=ToolType.HTTP, description="Make HTTP requests"),
}