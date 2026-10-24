from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from db import (
    add_candidate,
    get_candidates,
    get_candidate_by_id,
    update_candidate_status,
    delete_candidate,
    get_candidates_by_status,
    search_candidates,
    get_pipeline_stats,
    export_candidates_to_csv,
    import_candidates_from_csv,
)

console = Console()

STATUS_OPTIONS = {
    "1": "applied",
    "2": "screening",
    "3": "interviewing",
    "4": "offered",
    "5": "rejected",
}

STATUS_COLORS = {
    "applied": "cyan",
    "screening": "magenta",
    "interviewing": "yellow",
    "offered": "green",
    "rejected": "red",
}

def display_pipeline(candidates=None, title_suffix=""):
    if candidates is None:
        candidates = get_candidates()
    
    table_title = f"C2O Candidate Pipeline{title_suffix}"
    table = Table(title=table_title, header_style="bold magenta")
    table.add_column("ID", justify="center", style="bold cyan", no_wrap=True)
    table.add_column("Candidate Name", style="bold white")
    table.add_column("Email", style="dim")
    table.add_column("Target Role", style="bold green")
    table.add_column("Pipeline Status", justify="center")

    if not candidates:
        console.print("[dim]No candidates found matching the criteria.[/dim]\n")
        return

    for c in candidates:
        raw_status = c.get("status", "applied").lower()
        color = STATUS_COLORS.get(raw_status, "white")
        status_badge = f"[{color}]{raw_status.upper()}[/{color}]"
        
        table.add_row(
            str(c["id"]),
            c["full_name"],
            c["email"],
            c["role"],
            status_badge
        )

    console.print(table)
    console.print()

def display_candidate_details(cand_id: int):
    c = get_candidate_by_id(cand_id)
    if not c:
        console.print(f"\n[bold red]✗ Candidate #{cand_id} not found.[/bold red]\n")
        return

    raw_status = c.get("status", "applied").lower()
    color = STATUS_COLORS.get(raw_status, "white")
    status_badge = f"[{color}]{raw_status.upper()}[/{color}]"
    applied_on = c.get("created_at", "N/A")[:19].replace("T", " ")

    card_text = (
        f"[bold white]Full Name:[/bold white] {c['full_name']}\n"
        f"[bold white]Target Role:[/bold white] [bold green]{c['role']}[/bold green]\n"
        f"[bold white]Email Address:[/bold white] [dim]{c['email']}[/dim]\n"
        f"[bold white]Current Status:[/bold white] {status_badge}\n"
        f"[bold white]Applied At:[/bold white] [dim]{applied_on} UTC[/dim]"
    )
    console.print(Panel(card_text, title=f"[bold cyan]Candidate Profile #{cand_id}[/bold cyan]", border_style="cyan", expand=False))
    console.print()

def display_summary():
    stats, total = get_pipeline_stats()
    table = Table(title="Pipeline Summary & Analytics", header_style="bold blue")
    table.add_column("Hiring Stage", style="bold white")
    table.add_column("Candidate Count", justify="center", style="bold yellow")
    table.add_column("Pipeline Share", justify="right", style="cyan")

    for stage, count in stats.items():
        color = STATUS_COLORS.get(stage, "white")
        percentage = f"{(count / total * 100):.1f}%" if total > 0 else "0.0%"
        badge = f"[{color}]{stage.upper()}[/{color}]"
        table.add_row(badge, str(count), percentage)

    console.print(table)
    console.print(f"[bold green]Total Active Candidates:[/bold green] [bold white]{total}[/bold white]\n")

def prompt_status_selection():
    console.print("[dim][1] Applied  [2] Screening  [3] Interviewing  [4] Offered  [5] Rejected[/dim]")
    val = console.input("[cyan]Select new status (1-5): [/cyan]").strip()
    return STATUS_OPTIONS.get(val, val.lower())

def main():
    while True:
        console.print(
            Panel.fit(
                "[1] View Pipeline  •  [2] Add Candidate  •  [3] Update Status  •  [4] Delete Candidate  •  [5] Candidate Profile\n"
                "[6] Filter Status  •  [7] Search         •  [8] Pipeline Stats •  [9] Export CSV       •  [10] Import CSV  •  [11] Exit",
                title="[bold blue]C2O Recruitment Manager[/bold blue]",
                border_style="blue"
            )
        )

        choice = console.input("[bold yellow]Select an option (1-11): [/bold yellow]").strip()

        if choice == "1":
            display_pipeline()

        elif choice == "2":
            name = console.input("[cyan]Enter candidate full name: [/cyan]").strip()
            email = console.input("[cyan]Enter candidate email: [/cyan]").strip()
            role = console.input("[cyan]Enter candidate role: [/cyan]").strip()
            if name and email and role:
                add_candidate(name, email, role)
                console.print(f"\n[bold green]✓ Successfully added candidate {name}![/bold green]\n")
            else:
                console.print("\n[bold red]✗ Error: All fields are required.[/bold red]\n")

        elif choice == "3":
            try:
                cand_id = int(console.input("[cyan]Enter Candidate ID to update: [/cyan]").strip())
                new_status = prompt_status_selection()
                if new_status in STATUS_COLORS:
                    update_candidate_status(cand_id, new_status)
                    console.print(f"\n[bold green]✓ Updated candidate #{cand_id} to '{new_status}'![/bold green]\n")
                else:
                    console.print("\n[bold red]✗ Invalid status choice.[/bold red]\n")
            except ValueError:
                console.print("\n[bold red]✗ Error: Please enter a valid numerical ID.[/bold red]\n")

        elif choice == "4":
            try:
                cand_id = int(console.input("[red]Enter Candidate ID to delete: [/red]").strip())
                confirm = console.input(f"[bold red]Are you sure you want to delete #{cand_id}? (y/n): [/bold red]").strip().lower()
                if confirm == "y":
                    delete_candidate(cand_id)
                    console.print(f"\n[bold green]✓ Candidate #{cand_id} deleted successfully.[/bold green]\n")
                else:
                    console.print("\n[dim]Deletion canceled.[/dim]\n")
            except ValueError:
                console.print("\n[bold red]✗ Error: Please enter a valid numerical ID.[/bold red]\n")

        elif choice == "5":
            try:
                cand_id = int(console.input("[cyan]Enter Candidate ID to view profile: [/cyan]").strip())
                display_candidate_details(cand_id)
            except ValueError:
                console.print("\n[bold red]✗ Error: Please enter a valid numerical ID.[/bold red]\n")

        elif choice == "6":
            console.print("[dim][1] Applied  [2] Screening  [3] Interviewing  [4] Offered  [5] Rejected[/dim]")
            status_input = console.input("[cyan]Select status to filter by (1-5 or name): [/cyan]").strip()
            filter_status = STATUS_OPTIONS.get(status_input, status_input.lower())
            filtered = get_candidates_by_status(filter_status)
            display_pipeline(candidates=filtered, title_suffix=f" (Status: {filter_status.upper()})")

        elif choice == "7":
            search_query = console.input("[cyan]Enter search term (name, role, or email): [/cyan]").strip()
            if search_query:
                results = search_candidates(search_query)
                display_pipeline(candidates=results, title_suffix=f" (Search: '{search_query}')")
            else:
                console.print("\n[bold red]✗ Error: Search term cannot be empty.[/bold red]\n")

        elif choice == "8":
            display_summary()

        elif choice == "9":
            default_file = "candidates_pipeline.csv"
            user_filename = console.input(f"[cyan]Enter export filename (press Enter for '{default_file}'): [/cyan]").strip()
            target_name = user_filename if user_filename else default_file
            if not target_name.endswith(".csv"):
                target_name += ".csv"
            
            success, message = export_candidates_to_csv(target_name)
            if success:
                console.print(f"\n[bold green]✓ Successfully exported pipeline to '{message}'![/bold green]\n")
            else:
                console.print(f"\n[bold red]✗ Export failed: {message}[/bold red]\n")

        elif choice == "10":
            csv_path = console.input("[cyan]Enter path/name of CSV file to import: [/cyan]").strip()
            success, result = import_candidates_from_csv(csv_path)
            if success:
                console.print(f"\n[bold green]✓ Successfully imported {result} candidate(s) into Supabase![/bold green]\n")
            else:
                console.print(f"\n[bold red]✗ Import failed: {result}[/bold red]\n")

        elif choice == "11":
            console.print("[bold cyan]Exiting application. Goodbye![/bold cyan]")
            break

        else:
            console.print("\n[bold red]✗ Invalid selection. Please enter a number between 1 and 11.[/bold red]\n")

if __name__ == "__main__":
    main()