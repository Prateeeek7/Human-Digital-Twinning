import os
import sqlite3
import random
from datetime import datetime, timedelta
import json
from pathlib import Path

# Provide path to the db
DB_PATH = Path("data/clinical_patients.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def seed_database():
    print(f"Connecting to {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            demographics TEXT,
            baseline_vitals TEXT,
            baseline_labs TEXT,
            comorbidities TEXT,
            family_history TEXT,
            social_history TEXT,
            current_medications TEXT,
            active_status TEXT DEFAULT 'active',
            data_quality_score REAL,
            last_calibration_date TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            lab_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            reference_range TEXT,
            flag TEXT,
            source TEXT,
            page_number INTEGER,
            extraction_context TEXT,
            validated BOOLEAN DEFAULT 0,
            validation_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vital_signs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            vital_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            source TEXT,
            validated BOOLEAN DEFAULT 0,
            validation_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
    """)
    
    # 1. DELETE EXISTING IF EXISTS
    patient_id = "PT-001"
    cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM vital_signs WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM lab_values WHERE patient_id = ?", (patient_id,))
    
    # 2. INSERT PATIENT DEMOGRAPHICS
    demographics = {
        "name": "DOE, JOHN A.",
        "mrn": "MRN-8472910",
        "age": 65,
        "sex": "M",
        "dob": "1959-04-12",
        "weight": "82.5 kg",
        "height": "178 cm",
        "code_status": "FULL CODE",
        "allergies": ["Penicillin", "Sulfa"]
    }
    
    comorbidities = {
        "diabetes": True,
        "high_blood_pressure": True,
        "anaemia": False,
        "smoking": False
    }
    
    cursor.execute("""
        INSERT INTO patients (patient_id, demographics, comorbidities) 
        VALUES (?, ?, ?)
    """, (patient_id, json.dumps(demographics), json.dumps(comorbidities)))
    
    # 3. GENERATE 48 HOURS OF TIME SERIES DATA
    end_time = datetime.now()
    # Generate 1 point every 4 hours for 48 hours = 12 points
    
    # Starting base values
    base_hr = 85
    base_bp_sys = 140
    base_bp_dia = 90
    base_ef = 35
    base_cr = 1.2
    base_na = 140
    base_chol = 200
    
    for i in range(12, -1, -1):
        point_time = end_time - timedelta(hours=i*4)
        ts_str = point_time.isoformat()
        
        # Add some random walk noise
        hr = base_hr + random.randint(-4, 4)
        bp_sys = base_bp_sys + random.randint(-5, 5)
        ef = base_ef + random.randint(-1, 1)
        cr = base_cr + random.uniform(-0.1, 0.1)
        na = base_na + random.randint(-2, 2)
        chol = base_chol + random.randint(-5, 5)
        
        # Insert Vitals
        cursor.execute("INSERT INTO vital_signs (patient_id, timestamp, vital_name, value, unit) VALUES (?, ?, 'Heart Rate', ?, 'bpm')", (patient_id, ts_str, hr))
        cursor.execute("INSERT INTO vital_signs (patient_id, timestamp, vital_name, value, unit) VALUES (?, ?, 'Systolic BP', ?, 'mmHg')", (patient_id, ts_str, bp_sys))
        
        # Insert Labs (Maybe only once every 12 hours)
        if i % 3 == 0:
            cursor.execute("INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, 'Ejection Fraction', ?, '%')", (patient_id, ts_str, ef))
            cursor.execute("INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, 'Creatinine', ?, 'mg/dL')", (patient_id, ts_str, round(cr, 2)))
            cursor.execute("INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, 'Sodium', ?, 'mEq/L')", (patient_id, ts_str, na))
            cursor.execute("INSERT INTO lab_values (patient_id, timestamp, lab_name, value, unit) VALUES (?, ?, 'Cholesterol', ?, 'mg/dL')", (patient_id, ts_str, chol))

    conn.commit()
    print(f"Successfully seeded database with patient {patient_id} and 48 hours of time-series data.")
    conn.close()

if __name__ == "__main__":
    seed_database()
