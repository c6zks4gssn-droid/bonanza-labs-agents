#!/usr/bin/env python3
"""🤖 Bonanza Labs ✦ Agents CLI."""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="bonanza-agents")
def main():
    """🤖 Bonanza Labs ✦ Agents — AI agent orchestration."""
    pass


@main.command()
@click.option("--name", "-n", required=True, help="Agent name")
@click.option("--model", "-m", default="glm-5.1:cloud", help="LLM model")
@click.option("--budget", "-b", default=10.0, help="Budget limit in USD")
def create(name, model, budget):
    """Create a new agent."""
    from bonanza_agents.core.models import Agent, Tool, BUILT_IN_TOOLS
    agent = Agent(name=name, model=model, budget_limit_usd=budget, tools=list(BUILT_IN_TOOLS.values()))
    console.print(f"[bold green]✅ Agent created:[/] {agent.id}")
    console.print(f"   Name: {name} | Model: {model} | Budget: ${budget}")
    console.print(f"   Tools: {', '.join(BUILT_IN_TOOLS.keys())}")


@main.command()
def tools():
    """List available tools."""
    from bonanza_agents.core.models import BUILT_IN_TOOLS, ToolType
    table = Table(title="🛠️ Built-in Tools")
    table.add_column("Tool", style="bold")
    table.add_column("Type")
    table.add_column("Description")
    for t in BUILT_IN_TOOLS.values():
        table.add_row(t.name, t.type.value, t.description)
    console.print(table)


@main.command()
@click.option("--name", "-n", required=True, help="Workflow name")
def workflow(name):
    """Create a multi-agent workflow."""
    console.print(f"[bold]🔄 Workflow:[/] {name}")
    console.print("   Define steps in YAML config")
    console.print("   Run with: bonanza-agents run workflow.yaml")


@main.command()
def list_agents():
    """List all agents."""
    console.print("[bold]🤖 No agents yet.[/]")
    console.print("   Create one with: bonanza-agents create --name MyAgent")


if __name__ == "__main__":
    main()