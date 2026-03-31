from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import sqlite3
import os
import json
from pydantic import BaseModel
from datetime import datetime
import random
import csv

router = APIRouter()

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "hospital_core.db")
CLINICAL_DB_PATH = os.path.join(BASE_DIR, "data", "clinical_patients.db")
PATIENT_DB_DIR = os.path.join(BASE_DIR, "data", "PatientDatabase")
ALLERGENS_CSV_PATH = os.path.join(BASE_DIR, "food_ingredients_and_allergens.csv")
MEDS_CSV_PATH = os.path.join(BASE_DIR, "A_Z_medicines_dataset_of_India.csv")

# Ensure PatientDatabase directory exists
os.makedirs(PATIENT_DB_DIR, exist_ok=True)

# In-memory caches for fast autocomplete
MEDICINES_CACHE = []

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
from typing import List, Optional

class MedicationTiming(BaseModel):
    beforeBreakfast: bool
    afterBreakfast: bool
    beforeLunch: bool
    afterLunch: bool
    beforeDinner: bool
    afterDinner: bool

class MedicationEntry(BaseModel):
    name: str
    dosage: str
    timing: MedicationTiming

class NewEncounterModel(BaseModel):
    firstName: str
    lastName: str
    dob: str
    gender: str
    phone: str = ""
    address: str = ""
    allergies: str = ""
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
    diabetes: bool = False
    highBloodPressure: bool = False
    highCholesterol: bool = False
    anaemia: bool = False
    smoking: bool = False
    hba1c: Optional[str] = ""
    cholesterol: Optional[str] = ""
    hemoglobin: Optional[str] = ""
    medications: Optional[List[MedicationEntry]] = []

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
            "allergies": encounter.allergies,
            "code_status": "FULL CODE"
        }
        
        comorbidities = {
            "diabetes": encounter.diabetes,
            "high_blood_pressure": encounter.highBloodPressure,
            "high_cholesterol": encounter.highCholesterol,
            "anaemia": encounter.anaemia,
            "smoking": encounter.smoking
        }

        c_cursor.execute('''
            INSERT INTO patients (patient_id, demographics, comorbidities, active_status)
            VALUES (?, ?, ?, 'active')
        ''', (patient_id, json.dumps(demographics), json.dumps(comorbidities)))

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
            ("Ejection Fraction", float(encounter.ejectionFraction) if encounter.ejectionFraction else 0.0, "%"),
            ("Creatinine", float(encounter.creatinine) if encounter.creatinine else 0.0, "mg/dL"),
            ("Sodium", float(encounter.sodium) if encounter.sodium else 0.0, "mEq/L"),
            ("Potassium", float(encounter.potassium) if encounter.potassium else 0.0, "mEq/L"),
            ("BNP", float(encounter.bnp) if encounter.bnp else 0.0, "pg/mL")
        ]
        
        # Add conditional labs if provided
        if encounter.hba1c:
            l_list.append(("HbA1c", float(encounter.hba1c), "%"))
        if encounter.cholesterol:
            l_list.append(("Cholesterol", float(encounter.cholesterol), "mg/dL"))
        if encounter.hemoglobin:
            l_list.append(("Hemoglobin", float(encounter.hemoglobin), "g/dL"))

        for name, val, unit in l_list:
            c_cursor.execute(
                "INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, ?, ?, ?)",
                (patient_id, timestamp, name, val, unit)
            )

        # Medications
        if encounter.medications:
            for med in encounter.medications:
                # Convert timing dict to a comma-separated string for "frequency"
                t_dict = med.timing.dict()
                freq_tags = [k for k, v in t_dict.items() if v]
                freq_str = json.dumps(freq_tags) # Store as JSON array of true timings
                
                # We attempt to separate dosage number from unit, but since it's free text, just put in dosage_unit for now or let dosage be 0 and put all in dosage_unit
                c_cursor.execute('''
                    INSERT INTO medication_history 
                    (patient_id, medication_name, start_date, dosage, dosage_unit, frequency, source) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id, med.name, timestamp, 
                    1.0, med.dosage, freq_str, "Admission Intake"
                ))

        h_conn.commit()
        c_conn.commit()
        # ---------------------------------------------------------
        # 3. Write Isolated PatientDatabase JSON File
        # ---------------------------------------------------------
        isolated_twin = {
            "patient_id": patient_id,
            "mrn": mrn,
            "encounter_visit_id": visit_id,
            "admission_time": timestamp,
            "demographics": demographics,
            "comorbidities": comorbidities,
            "vitals": [{"timestamp": timestamp, "name": n, "value": v, "unit": u} for n, v, u in v_list],
            "labs": [{"timestamp": timestamp, "name": n, "value": v, "unit": u} for n, v, u in l_list],
            "medications": [
                {
                    "name": med.name,
                    "dosage": med.dosage,
                    "frequency": [k for k, val in med.timing.dict().items() if val],
                    "start_date": timestamp
                } for med in (encounter.medications or [])
            ]
        }
        
        patient_json_path = os.path.join(PATIENT_DB_DIR, f"{patient_id}.json")
        with open(patient_json_path, 'w', encoding='utf-8') as f:
            json.dump(isolated_twin, f, indent=4)

        return {"patient_id": patient_id, "mrn": mrn, "status": "success", "file": patient_json_path}
    except Exception as e:
        h_conn.rollback()
        c_conn.rollback()
        print(f"Error hydrating twin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        h_conn.close()
        c_conn.close()

# ---------------------------------------------------------
# Allergens & Medicines Data (From CSV)
# ---------------------------------------------------------

# ---------------------------------------------------------
# OCR Lab Ingest for an existing Patient Twin
# ---------------------------------------------------------
from fastapi import UploadFile, File

@router.post("/patients/{patient_id}/ingest-labs")
async def ingest_labs_from_document(patient_id: str, file: UploadFile = File(...)):
    """
    Upload a lab report / prescription image or PDF for an existing patient.
    Runs OCR, extracts lab values, writes them to the patient's timeline in the
    clinical database, and returns the structured lab data to the frontend.
    """
    import sys
    from pathlib import Path as PPath
    sys.path.insert(0, str(PPath(__file__).parent.parent.parent))

    from pdt.utils.ocr import DocumentOCR
    from pdt.utils.lab_report_parser import LabReportParser

    try:
        file_bytes = await file.read()
        doc_type = 'pdf' if (file.content_type and 'pdf' in file.content_type.lower()) or \
                           (file.filename and file.filename.lower().endswith('.pdf')) else 'image'

        # Run OCR
        ocr = DocumentOCR(use_easyocr=False)
        raw_text = ocr.extract_text_from_bytes(file_bytes, doc_type)

        # Parse lab values
        parser = LabReportParser()
        parsed = parser.parse(raw_text)
        lab_values = parsed.get('lab_values', {})

        if not lab_values:
            return {"status": "no_values", "message": "OCR ran but could not extract structured lab values.", "lab_values": {}}

        # Write to clinical DB under this patient's timeline
        timestamp = datetime.now().isoformat()
        c_conn = get_clinical_db_connection()
        c_cursor = c_conn.cursor()
        try:
            for lab_name, info in lab_values.items():
                value = info.get('value')
                unit = info.get('unit') or ''
                if value is None:
                    continue
                c_cursor.execute(
                    "INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, ?, ?, ?)",
                    (patient_id, timestamp, lab_name.replace('_', ' ').title(), float(value), unit)
                )
            c_conn.commit()
        finally:
            c_conn.close()

        # ---------------------------------------------------------
        # 3. Append to Isolated PatientDatabase JSON File
        # ---------------------------------------------------------
        patient_json_path = os.path.join(PATIENT_DB_DIR, f"{patient_id}.json")
        if os.path.exists(patient_json_path):
            with open(patient_json_path, 'r', encoding='utf-8') as f:
                try:
                    isolated_twin = json.load(f)
                except json.JSONDecodeError:
                    isolated_twin = None
                
            if isolated_twin and 'labs' in isolated_twin:
                for lab_name, info in lab_values.items():
                    value = info.get('value')
                    unit = info.get('unit') or ''
                    if value is not None:
                        isolated_twin['labs'].append({
                            "timestamp": timestamp,
                            "name": lab_name.replace('_', ' ').title(),
                            "value": float(value),
                            "unit": unit
                        })
                # Save it back
                with open(patient_json_path, 'w', encoding='utf-8') as f:
                    json.dump(isolated_twin, f, indent=4)
        # ---------------------------------------------------------

        # Build clean payload for the frontend
        structured = {
            lab_name: {"value": info.get('value'), "unit": info.get('unit') or ''}
            for lab_name, info in lab_values.items()
            if info.get('value') is not None
        }

        return {
            "status": "success",
            "patient_id": patient_id,
            "file_name": file.filename,
            "timestamp": timestamp,
            "lab_count": len(structured),
            "lab_values": structured,
        }

    except Exception as e:
        print(f"OCR ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/allergens")
async def get_allergens():
    """Returns a unique list of allergens extracted from food_ingredients_and_allergens.csv."""
    allergens_set = set()
    if os.path.exists(ALLERGENS_CSV_PATH):
        try:
            with open(ALLERGENS_CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    val = row.get("Allergens", "")
                    if val and val.lower() != "none":
                        # Some are comma separated like "Almonds, Wheat, Dairy"
                        parts = [p.strip() for p in val.split(",")]
                        for p in parts:
                            if p:
                                allergens_set.add(p)
        except Exception as e:
            print(f"Error reading allergens CSV: {e}")
    
    # Return sorted list
    return {"allergens": sorted(list(allergens_set))}

@router.get("/medicines")
async def get_medicines(q: str = ""):
    """Returns a fast autocomplete list of medicines based on query using in-memory cache."""
    global MEDICINES_CACHE
    if not MEDICINES_CACHE:
        # Load lazily into memory
        if os.path.exists(MEDS_CSV_PATH):
            try:
                # Structure: id,name,price,Is_discontinued,manufacturer...
                with open(MEDS_CSV_PATH, mode='r', encoding='utf-8') as f:
                    # just read line by line instead of dictreader to avoid memory overhead of full dicts
                    # We only care about name column (index 1)
                    next(f) # skip header
                    for line in f:
                        parts = line.split(',')
                        if len(parts) > 1:
                            name = parts[1].strip()
                            if name:
                                MEDICINES_CACHE.append(name)
            except Exception as e:
                print(f"Error reading medicines CSV: {e}")
                
    if not q:
        return {"medicines": []}

    q_lower = q.lower()
    matches = []
    # Find up to 20 matches instantly
    for med in MEDICINES_CACHE:
        # Simple substring match
        if q_lower in med.lower():
            matches.append(med)
            if len(matches) >= 20:
                break
                
    return {"medicines": matches}

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
