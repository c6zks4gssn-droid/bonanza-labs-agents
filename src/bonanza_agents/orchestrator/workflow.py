"""Workflow orchestrator — runs multi-agent workflows."""

from __future__ import annotations
from .models import Workflow, WorkflowStep, Task, TaskStatus
from .runtime.engine import AgentRuntime


class WorkflowOrchestrator:
    """Orchestrate multi-agent workflows."""

    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime

    async def run_workflow(self, workflow: Workflow, agents: dict[str, "Agent"]) -> Workflow:
        """Execute a workflow step by step."""
        workflow.status = TaskStatus.RUNNING
        results = {}

        for i, step in enumerate(workflow.steps):
            # Check condition
            if step.condition:
                try:
                    if not eval(step.condition, {"results": results}):
                        continue
                except Exception:
                    continue

            agent = agents.get(step.agent_id)
            if not agent:
                continue

            # Create and run task
            task = Task(agent_id=step.agent_id, prompt=step.prompt)
            task = await self.runtime.run_task(agent, task)
            results[step.id or str(i)] = task.result

            # Handle success/failure routing
            if task.status == TaskStatus.FAILED and step.on_failure == "stop":
                workflow.status = TaskStatus.FAILED
                return workflow

        workflow.status = TaskStatus.COMPLETED
        return workflow