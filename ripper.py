import json
import phonenumbers
import secrets
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

console = Console()
DATA = Path("reports.json")
EXPORT = Path("ripper-reports.txt")
VERSION = "7.0.0"

CATEGORIES = {
    "1": "Spam",
    "2": "Scam",
    "3": "Harassment",
    "4": "Impersonation",
    "5": "Other"
}


def load_reports():
    if DATA.exists():
        try:
            data = json.loads(DATA.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            console.print("[bold red]Could not read reports.json.[/bold red]")
    return []


def save_reports(reports):
    DATA.write_text(
        json.dumps(reports, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def banner():
    console.clear()
    console.print(
        Panel(
            "[bold white]𝐑𝐈𝐏𝐏𝐄𝐑 𝐖𝐀-𝐁𝐀𝐍[/bold white]\n"
            "[bold red]𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 & 𝐑𝐄𝐏𝐎𝐑𝐓𝐈𝐍𝐆 𝐒𝐘𝐒𝐓𝐄𝐌[/bold red]\n"
            "[dim]VERSION 7.0.0  |  DEV. RIPPER[/dim]",
            border_style="bright_red",
            box=box.DOUBLE,
            padding=(1, 3)
        )
    )


def pause():
    Prompt.ask("\n[bold red]Press Enter to return to command center[/bold red]")


def validate_number():
    number = Prompt.ask("[bold red]Enter international phone number")

    try:
        parsed = phonenumbers.parse(number, None)

        if not phonenumbers.is_possible_number(parsed):
            console.print("[red]Invalid number length.[/red]")
            return

        if not phonenumbers.is_valid_number(parsed):
            console.print("[yellow]Possible format, but not a valid number.[/yellow]")
            return

        console.print(Panel(
            f"[green]Valid phone-number format[/green]\n"
            f"International: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\n"
            f"Country: {phonenumbers.region_code_for_number(parsed)}\n"
            f"Country code: +{parsed.country_code}\n"
            f"National number: {parsed.national_number}\n\n"
            "[dim]This does not verify WhatsApp registration or account status.[/dim]",
            title="[bold red]NUMBER INTELLIGENCE[/bold red]",
            border_style="bright_red"
        ))

    except phonenumbers.NumberParseException:
        console.print("[red]Could not parse number. Include country code, e.g. +234.[/red]")


def choose_category():
    table = Table(box=box.SIMPLE_HEAVY, border_style="red")
    table.add_column("CODE", style="bold red")
    table.add_column("REPORT CATEGORY", style="white")

    for code, category in CATEGORIES.items():
        table.add_row(code, category)

    console.print(table)
    choice = Prompt.ask(
        "[bold red]Select category[/bold red]",
        choices=list(CATEGORIES.keys()),
        default="5"
    )
    return CATEGORIES[choice]


def create_report():
    console.print(Panel(
        "[white]Document suspicious activity accurately.[/white]\n"
        "[dim]Reports are saved locally on this device.[/dim]",
        title="[bold red]NEW INCIDENT RECORD[/bold red]",
        border_style="red"
    ))

    number = Prompt.ask("[bold red]Phone number").strip()
    if not number:
        console.print("[red]Phone number cannot be empty.[/red]")
        return

    category = choose_category()
    description = Prompt.ask("[bold red]Describe the incident").strip()

    if not description:
        console.print("[red]Description cannot be empty.[/red]")
        return

    reports = load_reports()

    report = {
        "id": "RIP-" + datetime.now().strftime("%Y%m%d") + "-"
              + secrets.token_hex(3).upper(),
        "number": number,
        "category": category,
        "description": description,
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "Pending",
        "notes": "",
        "evidence": ""
    }

    reports.append(report)
    save_reports(reports)

    console.print(Panel(
        f"[bold green]REPORT SAVED[/bold green]\n"
        f"Report ID: [white]{report['id']}[/white]\n"
        f"Category: {category}\n"
        f"Number: {number}",
        title="[bold red]RECORD CONFIRMED[/bold red]",
        border_style="green"
    ))


def show_report(report):
    console.print(Panel(
        f"[red]Report ID:[/red] {report.get('id', 'Legacy record')}\n"
        f"[red]Number:[/red] {report.get('number', 'Unknown')}\n"
        f"[red]Category:[/red] {report.get('category', 'Uncategorized')}\n"
        f"[red]Description:[/red] {report.get('description', 'No description')}\n"
        f"[red]Date:[/red] {report.get('date', 'Unknown')}",
        f"[red]Status:[/red] {report.get("status", "Pending")}\n"
        f"[red]Case notes:[/red] {report.get("notes") or "None"}\n"
        f"[red]Evidence:[/red] {report.get("evidence") or "None"}",
        title="[bold white]INCIDENT RECORD[/bold white]",
        border_style="bright_red"
    ))


def view_reports():
    reports = load_reports()

    if not reports:
        console.print("[yellow]No reports saved yet.[/yellow]")
        return

    for report in reports:
        show_report(report)


def search_reports():
    reports = load_reports()

    if not reports:
        console.print("[yellow]No reports available to search.[/yellow]")
        return

    query = Prompt.ask(
        "[bold red]Search number, report ID or category"
    ).strip().lower()

    if not query:
        console.print("[yellow]Search cannot be empty.[/yellow]")
        return

    matches = [
        report for report in reports
        if query in str(report.get("number", "")).lower()
        or query in str(report.get("id", "")).lower()
        or query in str(report.get("category", "Other")).lower()
    ]

    if not matches:
        console.print("[yellow]No matching records found.[/yellow]")
        return

    console.print(f"[green]{len(matches)} matching record(s) found.[/green]")
    for report in matches:
        show_report(report)


def export_reports():
    reports = load_reports()

    if not reports:
        console.print("[yellow]Nothing to export.[/yellow]")
        return

    with EXPORT.open("w", encoding="utf-8") as file:
        file.write("RIPPER WA-BAN - INCIDENT REPORT ARCHIVE\n")
        file.write("=" * 48 + "\n\n")

        for report in reports:
            file.write(
                f"REPORT ID: {report.get('id', 'Legacy record')}\n"
                f"NUMBER: {report.get('number', 'Unknown')}\n"
                f"CATEGORY: {report.get('category', 'Uncategorized')}\n"
                f"DESCRIPTION: {report.get('description', '')}\n"
                f"DATE: {report.get('date', 'Unknown')}\n"
                f"{'=' * 48}\n"
            )

    console.print(f"[bold green]Archive exported: {EXPORT}[/bold green]")


def dashboard():
    reports = load_reports()
    numbers = {
        str(report.get("number", ""))
        for report in reports if report.get("number")
    }

    latest = max(
        (str(report.get("date", "")) for report in reports),
        default="No reports yet"
    )

    table = Table(box=box.ROUNDED, border_style="bright_red")
    table.add_column("STATISTIC", style="bold red")
    table.add_column("VALUE", style="bold white")

    table.add_row("Total reports", str(len(reports)))
    table.add_row("Unique numbers", str(len(numbers)))
    table.add_row("Latest report", latest)
    table.add_row("Storage", "Local JSON")
    table.add_row(
        "Pending cases",
        str(sum(1 for r in reports if r.get("status", "Pending") == "Pending"))
    )
    table.add_row(
        "Reviewed cases",
        str(sum(1 for r in reports if r.get("status", "Pending") == "Reviewed"))
    )
    table.add_row(
        "Resolved cases",
        str(sum(1 for r in reports if r.get("status", "Pending") == "Resolved"))
    )

    console.print(Panel(
        table,
        title="[bold white]RIPPER CONTROL DASHBOARD[/bold white]",
        border_style="bright_red"
    ))

    category_table = Table(box=box.SIMPLE_HEAVY, border_style="red")
    category_table.add_column("CATEGORY", style="red")
    category_table.add_column("RECORDS", style="white", justify="right")

    for category in list(CATEGORIES.values()) + ["Uncategorized"]:
        count = sum(
            1 for report in reports
            if report.get("category", "Uncategorized") == category
        )
        category_table.add_row(category, str(count))

    console.print(Panel(
        category_table,
        title="[bold red]CATEGORY INTELLIGENCE[/bold red]",
        border_style="red"
    ))



def filter_category():
    category = choose_category()
    reports = load_reports()
    matches = [
        r for r in reports
        if r.get("category", "Uncategorized") == category
    ]

    console.print(f"[green]{len(matches)} record(s) in {category}.[/green]")
    for report in matches:
        show_report(report)


def view_by_id():
    report_id = Prompt.ask("[bold red]Enter report ID").strip().lower()
    matches = [
        r for r in load_reports()
        if str(r.get("id", "")).lower() == report_id
    ]

    if matches:
        show_report(matches[0])
    else:
        console.print("[yellow]Report ID not found.[/yellow]")


def delete_report():
    reports = load_reports()
    report_id = Prompt.ask("[bold red]Enter report ID to delete").strip().lower()

    matches = [
        r for r in reports
        if str(r.get("id", "")).lower() == report_id
    ]

    if not matches:
        console.print("[yellow]Report ID not found.[/yellow]")
        return

    show_report(matches[0])
    confirm = Prompt.ask(
        "[bold red]Permanently delete this report?[/bold red]",
        choices=["y", "n"],
        default="n"
    )

    if confirm == "y":
        reports.remove(matches[0])
        save_reports(reports)
        console.print("[green]Report deleted.[/green]")
    else:
        console.print("[yellow]Deletion cancelled.[/yellow]")


def export_json():
    reports = load_reports()

    if not reports:
        console.print("[yellow]Nothing to export.[/yellow]")
        return

    output = Path("ripper-reports.json")
    output.write_text(
        json.dumps(reports, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    console.print(f"[green]JSON archive exported to {output}[/green]")


def activity_summary():
    reports = load_reports()
    today = datetime.now().astimezone().date()
    recent = 0

    for report in reports:
        try:
            report_date = datetime.fromisoformat(
                report.get("date", "")
            ).date()
            if (today - report_date).days < 7:
                recent += 1
        except (ValueError, TypeError):
            pass

    table = Table(box=box.ROUNDED, border_style="bright_red")
    table.add_column("ACTIVITY", style="red")
    table.add_column("COUNT", style="bold white")
    table.add_row("All saved reports", str(len(reports)))
    table.add_row("Reports in last 7 days", str(recent))

    console.print(Panel(
        table,
        title="[bold red]ACTIVITY SUMMARY[/bold red]",
        border_style="bright_red"
    ))


def about():
    console.print(Panel(
        "[bold white]RIPPER WA-BAN[/bold white]\n"
        "[red]WhatsApp Security & Reporting Toolkit[/red]\n\n"
        "Developer: Dev. Ripper\n"
        f"Version: {VERSION}\n"
        "Storage: Local JSON\n\n"
        "[dim]Designed for documenting, organizing and exporting "
        "suspected abuse reports. It does not ban accounts or "
        "verify WhatsApp account status.[/dim]",
        title="[bold red]SYSTEM IDENTITY[/bold red]",
        border_style="bright_red"
    ))




# CASE MANAGEMENT 7.0

CASE_STATUSES = ["Pending", "Reviewed", "Resolved"]


def find_case():
    reports = load_reports()
    report_id = Prompt.ask("[bold red]Enter report ID").strip().upper()
    for report in reports:
        if str(report.get("id", "")).upper() == report_id:
            return reports, report
    console.print("[bold red]Report ID not found.[/bold red]")
    return reports, None


def update_case_status():
    reports, report = find_case()
    if report is None:
        return

    status = Prompt.ask(
        "[bold red]Select new status[/bold red]",
        choices=CASE_STATUSES
    )
    report["status"] = status
    save_reports(reports)
    console.print(f"[bold green]Case status updated to {status}.[/bold green]")


def edit_case_notes():
    reports, report = find_case()
    if report is None:
        return

    notes = Prompt.ask(
        "[bold red]Enter case notes[/bold red]"
    ).strip()
    report["notes"] = notes
    save_reports(reports)
    console.print("[bold green]Case notes saved.[/bold green]")


def add_evidence_reference():
    reports, report = find_case()
    if report is None:
        return

    reference = Prompt.ask(
        "[bold red]Enter evidence file path or URL[/bold red]"
    ).strip()
    if not reference:
        console.print("[yellow]No evidence reference entered.[/yellow]")
        return

    report["evidence"] = reference
    save_reports(reports)
    console.print("[bold green]Evidence reference saved.[/bold green]")


def filter_status():
    reports = load_reports()
    status = Prompt.ask(
        "[bold red]Filter by status[/bold red]",
        choices=CASE_STATUSES
    )

    matches = [
        report for report in reports
        if report.get("status", "Pending") == status
    ]

    console.print(f"[bold white]{len(matches)} case(s) — {status}[/bold white]")
    for report in matches:
        show_report(report)


def main():
    while True:
        banner()

        table = Table(box=box.HEAVY, border_style="bright_red")
        table.add_column("OPTION", style="bold red", justify="center")
        table.add_column("COMMAND", style="bold white")

        options = [
            ("1", "NUMBER INTELLIGENCE"),
            ("2", "CREATE INCIDENT REPORT"),
            ("3", "VIEW REPORT ARCHIVE"),
            ("4", "SEARCH RECORDS"),
            ("5", "EXPORT REPORT ARCHIVE"),
            ("6", "SYSTEM IDENTITY"),
            ("7", "CONTROL DASHBOARD"),
            ("8", "FILTER BY CATEGORY"),
            ("9", "VIEW REPORT BY ID"),
            ("10", "DELETE REPORT"),
            ("11", "EXPORT JSON ARCHIVE"),
            ("12", "ACTIVITY SUMMARY"),
            ("13", "UPDATE CASE STATUS"),
            ("14", "CASE NOTES"),
            ("15", "ADD EVIDENCE REFERENCE"),
            ("16", "FILTER BY STATUS"),
            ("0", "SHUT DOWN")
        ]

        for option, feature in options:
            table.add_row(option, feature)

        console.print(table)
        choice = Prompt.ask(
            "\n[bold red]RIPPER COMMAND[/bold red]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
        )

        if choice == "1":
            validate_number()
        elif choice == "2":
            create_report()
        elif choice == "3":
            view_reports()
        elif choice == "4":
            search_reports()
        elif choice == "5":
            export_reports()
        elif choice == "6":
            about()
        elif choice == "7":
            dashboard()
        elif choice == "8":
            filter_category()
        elif choice == "9":
            view_by_id()
        elif choice == "10":
            delete_report()
        elif choice == "11":
            export_json()
        elif choice == "12":
            activity_summary()
        elif choice == "13":
            update_case_status()
        elif choice == "14":
            edit_case_notes()
        elif choice == "15":
            add_evidence_reference()
        elif choice == "16":
            filter_status()
        elif choice == "0":
            console.print(
                Panel(
                    "[bold red]RIPPER SIGNING OFF.[/bold red]\n"
                    "[dim]SYSTEM SESSION TERMINATED[/dim]",
                    border_style="red"
                )
            )
            break

        pause()


if __name__ == "__main__":
    main()
