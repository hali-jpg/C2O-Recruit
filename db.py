import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_candidate(full_name: str, email: str, role: str, status: str = "applied"):
    """Insert a new candidate record into the candidates table."""
    data = {
        "full_name": full_name,
        "email": email,
        "role": role,
        "status": status
    }
    response = supabase.table("candidates").insert(data).execute()
    return response.data

def get_candidates():
    """Retrieve all candidates ordered by ID descending."""
    response = (
        supabase.table("candidates")
        .select("*")
        .order("id", desc=True)
        .execute()
    )
    return response.data

def get_candidate_by_id(candidate_id: int):
    """Retrieve a single candidate by their primary key ID."""
    response = (
        supabase.table("candidates")
        .select("*")
        .eq("id", candidate_id)
        .execute()
    )
    return response.data[0] if response.data else None

def update_candidate_status(candidate_id: int, new_status: str):
    """Update the status column of an existing candidate record."""
    response = (
        supabase.table("candidates")
        .update({"status": new_status})
        .eq("id", candidate_id)
        .execute()
    )
    return response.data

def delete_candidate(candidate_id: int):
    """Remove a candidate from the database by ID."""
    response = (
        supabase.table("candidates")
        .delete()
        .eq("id", candidate_id)
        .execute()
    )
    return response.data

def get_candidates_by_status(status: str):
    """Retrieve candidates filtered by their pipeline status."""
    response = (
        supabase.table("candidates")
        .select("*")
        .eq("status", status)
        .order("id", desc=True)
        .execute()
    )
    return response.data

def search_candidates(keyword: str):
    """Search candidates by name, role, or email."""
    term = keyword.strip()
    response = (
        supabase.table("candidates")
        .select("*")
        .or_(f'full_name.ilike."%{term}%",role.ilike."%{term}%",email.ilike."%{term}%"')
        .order("id", desc=True)
        .execute()
    )
    return response.data

def get_pipeline_stats():
    """Calculate counts per status and total candidates in the pipeline."""
    candidates = get_candidates()
    stats = {
        "applied": 0,
        "screening": 0,
        "interviewing": 0,
        "offered": 0,
        "rejected": 0,
    }
    for c in candidates:
        status = c.get("status", "applied").lower()
        stats[status] = stats.get(status, 0) + 1
    return stats, len(candidates)

def export_candidates_to_csv(filename: str = "candidates_pipeline.csv"):
    """Export all candidates to a local CSV file."""
    candidates = get_candidates()
    if not candidates:
        return False, "No candidate records to export."

    fieldnames = ["id", "full_name", "email", "role", "status", "created_at"]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(candidates)

    return True, filename

def import_candidates_from_csv(filepath: str):
    """Read candidates from a CSV file and batch insert them into Supabase."""
    if not os.path.exists(filepath):
        return False, f"File '{filepath}' not found."

    valid_statuses = {"applied", "screening", "interviewing", "offered", "rejected"}
    candidates_to_add = []

    with open(filepath, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("full_name", "").strip()
            email = row.get("email", "").strip()
            role = row.get("role", "").strip()
            status = row.get("status", "applied").strip().lower()
            if status not in valid_statuses:
                status = "applied"

            if name and email and role:
                candidates_to_add.append({
                    "full_name": name,
                    "email": email,
                    "role": role,
                    "status": status
                })

    if not candidates_to_add:
        return False, "No valid candidate entries found in CSV."

    response = supabase.table("candidates").insert(candidates_to_add).execute()
    return True, len(response.data)