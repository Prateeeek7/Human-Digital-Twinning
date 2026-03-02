from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import sqlite3
import os
import json
from pydantic import BaseModel

router = APIRouter()

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "hospital_core.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Hospital Core DB not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------------
# Master Patient Index (MPI)
# ---------------------------------------------------------
class PatientModel(BaseModel):
    id: str
    mrn: str
    first_name: str
    last_name: str
    dob: str
    gender: str
    phone: str
    address: str
    pcp_name: str

@router.get("/mpi", response_model=List[PatientModel])
async def get_patients(search: Optional[str] = Query(None)):
    """Search Master Patient Index globally by Name, MRN, or ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if search:
            query = f"%{search}%"
            cursor.execute('''
                SELECT * FROM patients 
                WHERE first_name LIKE ? OR last_name LIKE ? OR mrn LIKE ? OR id LIKE ?
                LIMIT 50
            ''', (query, query, query, query))
        else:
            cursor.execute('SELECT * FROM patients LIMIT 50')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

# ---------------------------------------------------------
# Bed Board (Encounters)
# ---------------------------------------------------------
@router.get("/bedboard")
async def get_bedboard(unit: Optional[str] = Query(None)):
    """Retrieve active inpatients, optionally filtered by unit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if unit:
            cursor.execute('''
                SELECT e.*, p.first_name, p.last_name, p.mrn, p.dob, p.gender 
                FROM encounters e 
                JOIN patients p ON e.patient_id = p.id
                WHERE e.unit = ? AND e.status = 'Admitted'
                ORDER BY e.room_bed
            ''', (unit,))
        else:
            cursor.execute('''
                SELECT e.*, p.first_name, p.last_name, p.mrn, p.dob, p.gender 
                FROM encounters e 
                JOIN patients p ON e.patient_id = p.id
                WHERE e.status = 'Admitted'
                ORDER BY e.unit, e.room_bed
            ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

# ---------------------------------------------------------
# Results Routing (Inbox)
# ---------------------------------------------------------
@router.get("/results")
async def get_provider_inbox(provider: str = Query("DR-SMITH")):
    """Get pending/final results routed to a specific provider."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT r.*, p.first_name, p.last_name, p.mrn 
            FROM results r
            JOIN patients p ON r.patient_id = p.id
            WHERE r.routed_to = ?
            ORDER BY r.result_time DESC
            LIMIT 100
        ''', (provider,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

# ---------------------------------------------------------
# Schedule (OR & Clinic)
# ---------------------------------------------------------
@router.get("/schedule")
async def get_daily_schedule(provider: str = Query("DR-SMITH")):
    """Get the provider's daily surgical and clinical schedule."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT s.*, p.first_name, p.last_name, p.mrn, p.dob
            FROM schedule s
            JOIN patients p ON s.patient_id = p.id
            WHERE s.provider = ?
            ORDER BY s.start_time ASC
        ''', (provider,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
