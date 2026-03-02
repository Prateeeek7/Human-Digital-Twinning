from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import sqlite3
import os
import json
from pydantic import BaseModel
from datetime import datetime
import random

router = APIRouter()

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "hospital_core.db")
CLINICAL_DB_PATH = os.path.join(BASE_DIR, "data", "clinical_patients.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Hospital Core DB not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_clinical_db_connection():
    if not os.path.exists(CLINICAL_DB_PATH):
        raise HTTPException(status_code=500, detail="Clinical Patients DB not found.")
    conn = sqlite3.connect(CLINICAL_DB_PATH)
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
# New Encounter (Digital Twin Hydration)
# ---------------------------------------------------------
class NewEncounterModel(BaseModel):
    firstName: str
    lastName: str
    dob: str
    gender: str
    phone: str = ""
    address: str = ""
    weightKg: str
    heightCm: str
    heartRate: str
    bpSys: str
    bpDia: str
    spo2: str
    respiratoryRate: str
    ejectionFraction: str
    creatinine: str
    sodium: str
    potassium: str
    bnp: str

@router.post("/encounter")
async def create_new_encounter(encounter: NewEncounterModel):
    """Initializes a new Digital Twin directly from live clinical parameters."""
    patient_id = f"PT-{random.randint(2000, 9999):04d}"
    mrn = f"MRN-{random.randint(1000000, 9999999)}"
    timestamp = datetime.now().isoformat()

    h_conn = get_db_connection()
    c_conn = get_clinical_db_connection()

    h_cursor = h_conn.cursor()
    c_cursor = c_conn.cursor()

    try:
        # 1. Write to Core Hospital DB (MPI)
        h_cursor.execute('''
            INSERT INTO patients (id, mrn, first_name, last_name, dob, gender, phone, address, pcp_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_id, mrn, encounter.firstName, encounter.lastName, 
            encounter.dob, encounter.gender, encounter.phone, encounter.address, "Dr. Smith (Attending)"
        ))

        visit_id = f"ENC-{random.randint(100000, 999999)}"
        h_cursor.execute('''
            INSERT INTO encounters (visit_id, patient_id, unit, room_bed, attending_physician, admission_time, status, acuity, chief_complaint)
            VALUES (?, ?, 'Cardiovascular ICU (CVICU)', 'C-101', 'DR-SMITH', ?, 'Admitted', 'Critical', 'Heart Failure Exacerbation')
        ''', (visit_id, patient_id, timestamp))

        # 2. Write to Clinical Patients DB (Digital Twin Time-Series Core)
        demographics = {
            "name": f"{encounter.lastName.upper()}, {encounter.firstName.upper()}",
            "mrn": mrn,
            "age": int((datetime.now() - datetime.strptime(encounter.dob, "%Y-%m-%d")).days / 365),
            "sex": encounter.gender,
            "dob": encounter.dob,
            "weight": f"{encounter.weightKg} kg",
            "height": f"{encounter.heightCm} cm",
            "code_status": "FULL CODE"
        }

        c_cursor.execute('''
            INSERT INTO patients (patient_id, demographics, active_status)
            VALUES (?, ?, 'active')
        ''', (patient_id, json.dumps(demographics)))

        # Vitals
        v_list = [
            ("Heart Rate", float(encounter.heartRate), "bpm"),
            ("Systolic BP", float(encounter.bpSys), "mmHg"),
            ("Diastolic BP", float(encounter.bpDia), "mmHg"),
            ("SpO2", float(encounter.spo2), "%"),
            ("Respiratory Rate", float(encounter.respiratoryRate), "breaths/min")
        ]
        for name, val, unit in v_list:
            c_cursor.execute(
                "INSERT INTO vital_signs (patient_id, timestamp, vital_name, value, unit) VALUES (?, ?, ?, ?, ?)",
                (patient_id, timestamp, name, val, unit)
            )

        # Labs
        l_list = [
            ("Ejection Fraction", float(encounter.ejectionFraction), "%"),
            ("Creatinine", float(encounter.creatinine), "mg/dL"),
            ("Sodium", float(encounter.sodium), "mEq/L"),
            ("Potassium", float(encounter.potassium), "mEq/L"),
            ("BNP", float(encounter.bnp), "pg/mL")
        ]
        for name, val, unit in l_list:
            c_cursor.execute(
                "INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, ?, ?, ?)",
                (patient_id, timestamp, name, val, unit)
            )

        h_conn.commit()
        c_conn.commit()
        
        return {"patient_id": patient_id, "mrn": mrn, "status": "success"}
    except Exception as e:
        h_conn.rollback()
        c_conn.rollback()
        print(f"Error hydrating twin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        h_conn.close()
        c_conn.close()

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

# ---------------------------------------------------------
# Provider Preferences
# ---------------------------------------------------------
class ProviderPreferencesModel(BaseModel):
    provider_id: str
    theme: str
    density: str
    alert_threshold_hr: int
    session_timeout_minutes: int

@router.get("/preferences/{provider_id}", response_model=ProviderPreferencesModel)
async def get_provider_preferences(provider_id: str):
    """Get the user interface and system preferences for a specific provider."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM provider_preferences
            WHERE provider_id = ?
        ''', (provider_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Preferences not found for provider")
        return dict(row)
    finally:
        conn.close()

@router.put("/preferences/{provider_id}", response_model=ProviderPreferencesModel)
async def update_provider_preferences(provider_id: str, prefs: ProviderPreferencesModel):
    """Update the user interface and system preferences for a specific provider."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE provider_preferences
            SET theme = ?, density = ?, alert_threshold_hr = ?, session_timeout_minutes = ?
            WHERE provider_id = ?
        ''', (prefs.theme, prefs.density, prefs.alert_threshold_hr, prefs.session_timeout_minutes, provider_id))
        
        if cursor.rowcount == 0:
            # If standard update failed, the provider might not exist yet, let's insert
            cursor.execute('''
                INSERT INTO provider_preferences (provider_id, theme, density, alert_threshold_hr, session_timeout_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (provider_id, prefs.theme, prefs.density, prefs.alert_threshold_hr, prefs.session_timeout_minutes))
            
        conn.commit()
        return dict(prefs)
    finally:
        conn.close()
