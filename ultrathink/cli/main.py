"""Ultrathink CLI - ADHD-friendly task management"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint
import httpx
from typing import Optional
from datetime import datetime

app = typer.Typer(
    name="ultra",
    help="🧠 Ultrathink - ADHD-friendly AI task management for TickTick",
    add_completion=False,
)

console = Console()
API_BASE = "http://192.168.1.87:8001"


def get_api_client():
    """Get HTTP client for API requests"""
    return httpx.Client(base_url=API_BASE, timeout=30.0)


def handle_api_error(response: httpx.Response):
    """Handle API errors gracefully"""
    if response.status_code == 401:
        console.print("[red]❌ Not authenticated. Run 'ultra auth' first.[/red]")
        raise typer.Exit(1)
    elif response.status_code >= 400:
        console.print(f"[red]❌ Error: {response.text}[/red]")
        raise typer.Exit(1)


@app.command()
def auth():
    """Authenticate with TickTick"""
    console.print("[cyan]🔐 Authenticating with TickTick...[/cyan]")

    client = get_api_client()
    response = client.get("/auth/login")

    if response.status_code == 200:
        auth_url = response.json()["auth_url"]
        console.print(f"\n[green]Please open this URL in your browser:[/green]")
        console.print(f"[blue]{auth_url}[/blue]\n")
        console.print("[yellow]After authorizing, you'll be redirected and authenticated.[/yellow]")
    else:
        handle_api_error(response)


@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Task description"),
    no_breakdown: bool = typer.Option(False, "--no-breakdown", help="Skip AI breakdown"),
):
    """Add a new task with AI breakdown"""

    with console.status("[cyan]Creating task and analyzing with AI...[/cyan]"):
        client = get_api_client()
        response = client.post(
            "/tasks",
            json={
                "title": title,
                "description": description,
                "auto_breakdown": not no_breakdown,
            },
        )

    if response.status_code >= 400:
        handle_api_error(response)

    data = response.json()
    task = data["task"]
    analysis = data["analysis"]

    console.print(f"\n[green]✅ Task created:[/green] {task['title']}")

    if analysis.get("breakdown"):
        breakdown = analysis["breakdown"]

        console.print(f"\n[cyan]🤖 AI Analysis:[/cyan]")
        console.print(f"  Energy: {analysis['energy_level']}")
        console.print(f"  Estimated time: {analysis['estimated_minutes']} minutes")
        console.print(f"  Cognitive load: {breakdown.get('cognitive_load', 'moderate')}")

        console.print(f"\n[yellow]💡 First step:[/yellow] {breakdown.get('first_step', '')}")

        if breakdown.get("subtasks"):
            console.print(f"\n[cyan]📋 Subtasks created:[/cyan]")
            for i, subtask in enumerate(breakdown["subtasks"], 1):
                energy_icon = {
                    "low": "🟢",
                    "medium": "🟡",
                    "high": "🔴"
                }.get(subtask.get("energy", "medium"), "⚪")

                console.print(
                    f"  {i}. {energy_icon} {subtask['title']} "
                    f"({subtask.get('estimated_minutes', '?')}min)"
                )

        if breakdown.get("tips"):
            console.print(f"\n[blue]💭 Tips:[/blue] {breakdown['tips']}")


@app.command(name="list")
def list_tasks(
    energy: Optional[str] = typer.Option(None, "--energy", "-e", help="Filter by energy level (low/medium/high)"),
    completed: bool = typer.Option(False, "--completed", "-c", help="Show completed tasks"),
):
    """List tasks with AI insights"""

    params = {}
    if energy:
        params["energy_level"] = energy
    if completed:
        params["completed"] = True

    with console.status("[cyan]Fetching tasks...[/cyan]"):
        client = get_api_client()
        response = client.get("/tasks", params=params)

    if response.status_code >= 400:
        handle_api_error(response)

    tasks = response.json()

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title=f"Tasks ({len(tasks)})")
    table.add_column("Title", style="cyan")
    table.add_column("Energy", justify="center")
    table.add_column("Time", justify="right")
    table.add_column("Priority", justify="center")

    for task in tasks:
        insights = task.get("ai_insights", {})

        energy_icon = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴"
        }.get(insights.get("energy_level", "medium"), "⚪")

        time_str = f"{insights.get('estimated_minutes', '?')}min"

        priority_score = insights.get("priority_score", 50)
        if priority_score >= 80:
            priority = "🔴 High"
        elif priority_score >= 50:
            priority = "🟡 Med"
        else:
            priority = "🟢 Low"

        table.add_row(
            task["title"],
            energy_icon,
            time_str,
            priority,
        )

    console.print(table)


@app.command()
def work(
    energy: str = typer.Option("medium", "--energy", "-e", help="Your current energy level"),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of tasks to show"),
):
    """Get task suggestions for your current energy level"""

    with console.status(f"[cyan]Finding {energy} energy tasks...[/cyan]"):
        client = get_api_client()
        response = client.get(
            "/energy/suggest-tasks",
            params={"energy_level": energy, "limit": limit},
        )

    if response.status_code >= 400:
        handle_api_error(response)

    tasks = response.json()

    if not tasks:
        console.print(f"[yellow]No {energy} energy tasks found.[/yellow]")
        return

    energy_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}[energy]
    console.print(f"\n{energy_emoji} [cyan]Tasks matching your {energy} energy:[/cyan]\n")

    for i, task in enumerate(tasks, 1):
        console.print(f"{i}. [bold]{task['title']}[/bold]")
        console.print(f"   ⏱️  {task.get('estimated_minutes', '?')} minutes")

        if task.get('first_step'):
            console.print(f"   💡 Start with: {task['first_step']}")

        console.print()


@app.command()
def done(
    task_title: str = typer.Argument(..., help="Task title (or part of it)"),
    time: Optional[int] = typer.Option(None, "--time", "-t", help="Actual time spent (minutes)"),
):
    """Mark a task as complete"""

    # First, find the task
    with console.status("[cyan]Finding task...[/cyan]"):
        client = get_api_client()
        response = client.get("/tasks")

    if response.status_code >= 400:
        handle_api_error(response)

    tasks = response.json()
    matching_tasks = [t for t in tasks if task_title.lower() in t["title"].lower()]

    if not matching_tasks:
        console.print(f"[red]No tasks found matching '{task_title}'[/red]")
        return

    if len(matching_tasks) > 1:
        console.print(f"[yellow]Multiple tasks found. Please be more specific:[/yellow]")
        for t in matching_tasks:
            console.print(f"  - {t['title']}")
        return

    task = matching_tasks[0]
    task_id = task["id"]

    # Complete the task
    with console.status("[cyan]Completing task...[/cyan]"):
        params = {}
        if time:
            params["actual_minutes"] = time

        response = client.post(f"/tasks/{task_id}/complete", params=params)

    if response.status_code >= 400:
        handle_api_error(response)

    console.print(f"[green]✅ Completed:[/green] {task['title']}")

    if time:
        console.print(f"[blue]⏱️  Time spent: {time} minutes[/blue]")


@app.command()
def daily():
    """Get your daily review and top priorities"""

    with console.status("[cyan]Preparing your daily review...[/cyan]"):
        client = get_api_client()
        response = client.get("/daily")

    if response.status_code >= 400:
        handle_api_error(response)

    data = response.json()

    console.print(f"\n[bold cyan]📅 Daily Review - {data['date']}[/bold cyan]\n")

    # Recommended energy
    energy_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🔴"
    }.get(data['recommended_energy'], "⚪")

    console.print(f"{energy_emoji} [cyan]Predicted energy:[/cyan] {data['recommended_energy']}")
    console.print()

    # Top priorities
    if data.get("top_priorities"):
        console.print("[bold yellow]🎯 Top 3 Priorities:[/bold yellow]")
        for i, task in enumerate(data["top_priorities"], 1):
            console.print(f"  {i}. {task['title']} ({task.get('estimated_minutes', '?')}min)")
        console.print()

    # Due today
    if data.get("due_today"):
        console.print(f"[bold red]⏰ Due Today ({len(data['due_today'])}):[/bold red]")
        for task in data["due_today"]:
            console.print(f"  - {task['title']}")
        console.print()

    # Stale tasks
    if data.get("stale_tasks"):
        console.print(f"[bold magenta]⚠️  Stale Tasks ({len(data['stale_tasks'])}):[/bold magenta]")
        for task in data["stale_tasks"][:3]:
            console.print(f"  - {task['task_title']} ({task['days_stale']} days old)")
            if task.get("unstuck_help", {}).get("tiny_first_step"):
                console.print(f"    💡 {task['unstuck_help']['tiny_first_step']}")
        console.print()

    console.print(f"[green]{data.get('message', 'Have a productive day!')}[/green]")


@app.command()
def detail(
    task_title: str = typer.Argument(..., help="Task title (or part of it)"),
):
    """Get detailed AI insights for a task"""

    # Find the task
    with console.status("[cyan]Finding task...[/cyan]"):
        client = get_api_client()
        response = client.get("/tasks")

    if response.status_code >= 400:
        handle_api_error(response)

    tasks = response.json()
    matching_tasks = [t for t in tasks if task_title.lower() in t["title"].lower()]

    if not matching_tasks:
        console.print(f"[red]No tasks found matching '{task_title}'[/red]")
        return

    if len(matching_tasks) > 1:
        console.print(f"[yellow]Multiple tasks found. Please be more specific:[/yellow]")
        for t in matching_tasks:
            console.print(f"  - {t['title']}")
        return

    task = matching_tasks[0]
    task_id = task["id"]

    # Get details
    with console.status("[cyan]Fetching AI insights...[/cyan]"):
        response = client.get(f"/tasks/{task_id}")

    if response.status_code >= 400:
        handle_api_error(response)

    data = response.json()
    insights = data.get("insights", {})

    # Display
    console.print(f"\n[bold cyan]📋 {insights.get('task_title', task['title'])}[/bold cyan]\n")

    if insights.get("energy_level"):
        energy_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}[insights["energy_level"]]
        console.print(f"{energy_emoji} Energy: {insights['energy_level']}")

    if insights.get("estimated_minutes"):
        console.print(f"⏱️  Estimated: {insights['estimated_minutes']} minutes")

    if insights.get("cognitive_load"):
        console.print(f"🧠 Cognitive load: {insights['cognitive_load']}")

    if insights.get("eisenhower_quadrant"):
        console.print(f"📊 Priority: {insights['eisenhower_quadrant']}")

    # Breakdown
    if insights.get("breakdown"):
        breakdown = insights["breakdown"]

        if breakdown.get("first_step"):
            console.print(f"\n[yellow]💡 First step:[/yellow] {breakdown['first_step']}")

        if breakdown.get("subtasks"):
            console.print(f"\n[cyan]📋 Subtasks:[/cyan]")
            for i, subtask in enumerate(breakdown["subtasks"], 1):
                energy_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(
                    subtask.get("energy", "medium"), "⚪"
                )
                console.print(f"  {i}. {energy_icon} {subtask['title']}")

    # Stale task help
    if insights.get("days_since_created", 0) >= 3:
        console.print(f"\n[magenta]⚠️  This task is {insights['days_since_created']} days old[/magenta]")

        if insights.get("blockers"):
            console.print(f"[yellow]Possible blockers:[/yellow]")
            for blocker in insights["blockers"]:
                console.print(f"  - {blocker}")


@app.command()
def prioritize():
    """Re-prioritize all your tasks using AI"""

    with console.status("[cyan]🤖 Analyzing and prioritizing all tasks...[/cyan]"):
        client = get_api_client()
        response = client.post("/tasks/prioritize")

    if response.status_code >= 400:
        handle_api_error(response)

    tasks = response.json()

    console.print(f"\n[green]✅ Prioritized {len(tasks)} tasks[/green]\n")

    # Show top 5
    console.print("[bold cyan]🎯 Top 5 Priorities:[/bold cyan]\n")
    for i, task in enumerate(tasks[:5], 1):
        priority_data = task.get("priority_data", {})
        score = priority_data.get("priority_score", 0)
        quadrant = priority_data.get("eisenhower_quadrant", "?")

        console.print(f"{i}. [bold]{task['title']}[/bold]")
        console.print(f"   Score: {score}/100 | Quadrant: {quadrant}")
        console.print(f"   {priority_data.get('reasoning', '')}\n")


@app.command()
def unstuck():
    """Find stale tasks and get help overcoming procrastination"""

    with console.status("[cyan]Finding stale tasks...[/cyan]"):
        client = get_api_client()
        response = client.get("/tasks/analyze/stale")

    if response.status_code >= 400:
        handle_api_error(response)

    stale_tasks = response.json()

    if not stale_tasks:
        console.print("[green]✅ No stale tasks! You're doing great![/green]")
        return

    console.print(f"\n[yellow]Found {len(stale_tasks)} tasks needing attention:[/yellow]\n")

    for task in stale_tasks:
        console.print(f"[bold]{task['task_title']}[/bold]")
        console.print(f"  Days sitting: {task['days_stale']}")

        help_data = task.get("unstuck_help", {})

        if help_data.get("tiny_first_step"):
            console.print(f"  💡 Tiny first step: {help_data['tiny_first_step']}")

        if help_data.get("reframe"):
            console.print(f"  🔄 Reframe: {help_data['reframe']}")

        if help_data.get("encouragement"):
            console.print(f"  💪 {help_data['encouragement']}")

        console.print()


@app.command()
def energy(
    level: str = typer.Argument(..., help="Your current energy level (low/medium/high)"),
    focus: Optional[str] = typer.Option(None, "--focus", help="Focus quality (scattered/moderate/focused)"),
):
    """Log your current energy level"""

    with console.status("[cyan]Logging energy level...[/cyan]"):
        client = get_api_client()
        response = client.post(
            "/energy/log",
            json={"energy_level": level, "focus_quality": focus},
        )

    if response.status_code >= 400:
        handle_api_error(response)

    energy_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}[level]
    console.print(f"{energy_emoji} [green]Energy logged:[/green] {level}")

    # Show task suggestions
    console.print(f"\n[cyan]Here are some {level} energy tasks you could work on:[/cyan]")

    response = client.get(
        "/energy/suggest-tasks",
        params={"energy_level": level, "limit": 3},
    )

    if response.status_code == 200:
        tasks = response.json()
        for i, task in enumerate(tasks, 1):
            console.print(f"  {i}. {task['title']} ({task.get('estimated_minutes', '?')}min)")


@app.command()
def analyze():
    """Analyze all existing TickTick tasks with AI"""

    with console.status("[cyan]🤖 Analyzing all your TickTick tasks with AI...[/cyan]"):
        # Use extended timeout for bulk analysis (5 minutes)
        client = httpx.Client(base_url=API_BASE, timeout=300.0)
        response = client.post("/tasks/analyze-all")

    if response.status_code >= 400:
        handle_api_error(response)

    data = response.json()

    console.print(f"\n[green]✅ Analysis complete![/green]")
    console.print(f"  [cyan]Analyzed:[/cyan] {data['analyzed']} tasks")
    console.print(f"  [yellow]Skipped (already analyzed):[/yellow] {data['skipped']} tasks")
    console.print(f"  [blue]Total tasks:[/blue] {data['total']}")

    console.print(f"\n[green]Your tasks now have AI insights for energy levels, time estimates, and priorities![/green]")


if __name__ == "__main__":
    app()
