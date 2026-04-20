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


@main.command()
def avatars():
    """List available HeyGen avatars."""
    try:
        from bonanza_agents.tools.avatar import HeyGenClient
        client = HeyGenClient()
        avatars = client.list_avatars()
        if not avatars:
            console.print("[yellow]No avatars found. Set HEYGEN_API_KEY.[/]")
            return
        table = Table(title="🎭 Available Avatars")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Gender")
        table.add_column("Type")
        for a in avatars[:10]:
            table.add_row(a.avatar_id[:12] + "...", a.name, a.gender, a.type)
        console.print(table)
    except ValueError as e:
        console.print(f"[red]{e}[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")


@main.command()
@click.argument("script")
@click.option("--anchor", "-a", default="female_pro", help="Anchor preset (female_pro, male_pro, female_casual, male_casual)")
@click.option("--format", "-f", default="16:9", help="Aspect ratio (16:9, 9:16)")
@click.option("--bg", default="#0a0a0f", help="Background hex color")
def news(script, anchor, format, bg):
    """Create an AI news video with human avatar."""
    try:
        from bonanza_agents.tools.avatar import HeyGenClient
        client = HeyGenClient()
        console.print(f"[bold]🎬 Creating news video...[/]")
        console.print(f"   Anchor: {anchor} | Format: {format}")
        result = client.create_news_video(script=script, anchor=anchor, aspect_ratio=format, background=bg)
        if result.error:
            console.print(f"[red]❌ {result.error}[/]")
            return
        console.print(f"[green]✅ Video created![/] ID: {result.video_id}")
        console.print(f"   Status: {result.status}")
        console.print(f"   Poll with: bonanza-agents status {result.video_id}")
    except ValueError as e:
        console.print(f"[red]{e}[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")


@main.command()
@click.argument("video_id")
def status(video_id):
    """Check video generation status."""
    try:
        from bonanza_agents.tools.avatar import HeyGenClient
        client = HeyGenClient()
        result = client.get_video_status(video_id)
        console.print(f"Video: {result.video_id}")
        console.print(f"Status: {result.status}")
        if result.video_url:
            console.print(f"[green]URL: {result.video_url}[/]")
        if result.thumbnail_url:
            console.print(f"Thumbnail: {result.thumbnail_url}")
        if result.error:
            console.print(f"[red]Error: {result.error}[/]")
    except ValueError as e:
        console.print(f"[red]{e}[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")


if __name__ == "__main__":
    main()