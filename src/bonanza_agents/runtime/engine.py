"""Agent runtime — executes tasks using LLM + tools."""

from __future__ import annotations
import json
import httpx
from typing import Optional
from bonanza_agents.core.models import Agent, Task, TaskStatus, ToolType


class AgentRuntime:
    """Run agent tasks with LLM calls and tool execution."""

    def __init__(self, ollama_base: str = "http://localhost:11434"):
        self.ollama_base = ollama_base

    async def run_task(self, agent: Agent, task: Task) -> Task:
        """Execute a task with an agent."""
        task.status = TaskStatus.RUNNING

        # Build messages
        messages = [{"role": "system", "content": agent.system_prompt}]
        messages.append({"role": "user", "content": task.prompt})

        # Add tool descriptions to system prompt
        if agent.tools:
            tool_descs = "\n".join(f"- {t.name}: {t.description}" for t in agent.tools if t.enabled)
            messages[0]["content"] += f"\n\nAvailable tools:\n{tool_descs}"

        # Call LLM
        try:
            result = await self._call_llm(agent.model, agent.provider, messages)
            task.result = result
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.result = f"Error: {e}"
            task.status = TaskStatus.FAILED

        return task

    async def _call_llm(self, model: str, provider: str, messages: list[dict]) -> str:
        """Call the LLM via Ollama."""
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.ollama_base}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
            )
            if resp.status_code == 200:
                return resp.json()["message"]["content"]
            raise Exception(f"LLM error: {resp.status_code} {resp.text[:200]}")

    async def execute_tool(self, tool_name: str, params: dict) -> dict:
        """Execute a built-in tool."""
        if tool_name == "search":
            return await self._tool_search(params)
        elif tool_name == "video":
            return await self._tool_video(params)
        elif tool_name == "wallet":
            return await self._tool_wallet(params)
        elif tool_name == "webhook":
            return await self._tool_webhook(params)
        elif tool_name == "http":
            return await self._tool_http(params)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _tool_search(self, params: dict) -> dict:
        """Search the web (placeholder — will use Bonanza Search)."""
        return {"status": "not_implemented", "note": "Install bonanza-search for web search"}

    async def _tool_video(self, params: dict) -> dict:
        """Generate a video (placeholder — will use FrameForge)."""
        return {"status": "not_implemented", "note": "Install bonanza-labs[video] for video generation"}

    async def _tool_wallet(self, params: dict) -> dict:
        """Send a payment (placeholder — will use Agent Wallet)."""
        return {"status": "not_implemented", "note": "Install agent-wallet for payments"}

    async def _tool_webhook(self, params: dict) -> dict:
        """Send a webhook."""
        url = params.get("url", "")
        payload = params.get("payload", {})
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            return {"status_code": resp.status_code, "body": resp.text[:500]}

    async def _tool_http(self, params: dict) -> dict:
        """Make an HTTP request."""
        method = params.get("method", "GET").upper()
        url = params.get("url", "")
        headers = params.get("headers", {})
        body = params.get("body")
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(method, url, headers=headers, json=body)
            return {"status_code": resp.status_code, "body": resp.text[:1000]}