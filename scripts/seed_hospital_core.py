import sqlite3
import os
import json
import random
from datetime import datetime, timedelta
try:
    from faker import Faker
except ImportError:
    print("Please install faker: pip install Faker")
    exit(1)

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "hospital_core.db")

print(f"Creating Unified Hospital Database at: {DB_PATH}")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Remove old DB if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
fake = Faker('en_IN')

# ---------------------------------------------------------
# 1. Master Patient Index (MPI)
# ---------------------------------------------------------
print("Creating 'patients' (MPI) table...")
cursor.execute('''
CREATE TABLE patients (
    id TEXT PRIMARY KEY,
    mrn TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    dob TEXT NOT NULL,
    gender TEXT,
    phone TEXT,
    address TEXT,
    pcp_name TEXT
)
''')

def generate_mrn():
    return f"MRN-{fake.random_int(min=1000000, max=9999999)}"

print("Seeding 1000 patients into MPI...")
patient_ids = []
for i in range(1000):
    pid = f"PT-{i+1:04d}"
    patient_ids.append(pid)
    gender = random.choice(['M', 'F', 'O'])
    first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
    
    # Generate age distributions skewed older for a hospital
    age_days = random.randint(18 * 365, 90 * 365)
    dob = (datetime.now() - timedelta(days=age_days)).strftime("%Y-%m-%d")
    
    cursor.execute('''
    INSERT INTO patients (id, mrn, first_name, last_name, dob, gender, phone, address, pcp_name)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pid,
        generate_mrn(),
        first_name,
        fake.last_name(),
        dob,
        gender,
        fake.phone_number()[:15],
        fake.address().replace("\n", ", "),
        f"Dr. {fake.last_name()}"
    ))

# Ensure our specific test patient PT-001 matches the existing twin dashboard demographics
cursor.execute('''
UPDATE patients 
SET first_name = 'Rajesh', last_name = 'Kumar', dob = '1959-05-14', gender = 'M', pcp_name = 'Dr. Sarah Sharma'
WHERE id = 'PT-001'
''')

# ---------------------------------------------------------
# 2. Bed Board (Encounters)
# ---------------------------------------------------------
print("Creating 'encounters' (Bed Board) table...")
cursor.execute('''
CREATE TABLE encounters (
    visit_id TEXT PRIMARY KEY,
    patient_id TEXT,
    unit TEXT,
    room_bed TEXT,
    attending_physician TEXT,
    admission_time TEXT,
    status TEXT,
    acuity TEXT,
    chief_complaint TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
''')

units = [
    {"name": "Medical Intensive Care Unit (MICU)", "rooms": 20, "prefix": "M"},
    {"name": "Surgical Intensive Care Unit (SICU)", "rooms": 15, "prefix": "S"},
    {"name": "Cardiovascular ICU (CVICU)", "rooms": 12, "prefix": "C"},
    {"name": "East Wing Telemetry", "rooms": 40, "prefix": "E"},
    {"name": "West Wing Med/Surg", "rooms": 60, "prefix": "W"}
]

print("Seeding 65 active inpatient encounters for Bed Board...")
active_patients = random.sample(patient_ids, 65)

# Ensure PT-001 is on the board
if 'PT-001' not in active_patients:
    active_patients[0] = 'PT-001'

for i, pid in enumerate(active_patients):
    visit_id = f"ENC-{fake.random_int(min=100000, max=999999)}"
    unit_obj = random.choice(units)
    room = f"{unit_obj['prefix']}-{random.randint(100, 100 + unit_obj['rooms'])}"
    
    # Admission time within the last 5 days
    admit_dt = datetime.now() - timedelta(hours=random.randint(1, 120))
    
    acuity = random.choice(["Critical", "High", "Moderate", "Stable"]) if "ICU" in unit_obj['name'] else random.choice(["Moderate", "Stable", "Pending Discharge"])
    
    complaints = ["Shortness of breath", "Chest Pain", "Altered Mental Status", "Sepsis", "Post-op Monitoring", "Heart Failure Exacerbation", "Pneumonia", "Fall / Trauma"]
    
    cursor.execute('''
    INSERT INTO encounters (visit_id, patient_id, unit, room_bed, attending_physician, admission_time, status, acuity, chief_complaint)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        visit_id,
        pid,
        unit_obj["name"],
        room,
        f"Dr. {fake.last_name()}",
        admit_dt.isoformat() + "Z",
        "Admitted",
        acuity,
        random.choice(complaints)
    ))

# Make PT-001 predictable
cursor.execute('''
UPDATE encounters 
SET unit = 'Cardiovascular ICU (CVICU)', room_bed = 'C-104', acuity = 'Critical', chief_complaint = 'Decompensated Heart Failure', attending_physician = 'Dr. T. Barnaby'
WHERE patient_id = 'PT-001'
''')


# ---------------------------------------------------------
# 3. Results Routing (Inbox)
# ---------------------------------------------------------
print("Creating 'results' (Inbox) table...")
cursor.execute('''
CREATE TABLE results (
    result_id TEXT PRIMARY KEY,
    patient_id TEXT,
    order_type TEXT,
    panel_name TEXT,
    result_details TEXT,
    status TEXT,
    flag TEXT,
    result_time TEXT,
    routed_to TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
''')

print("Seeding 150 incoming results for the current provider...")
for i in range(150):
    pid = random.choice(patient_ids)
    order_type = random.choice(["Lab", "Lab", "Lab", "Imaging", "Microbiology"])
    
    res_time = datetime.now() - timedelta(minutes=random.randint(5, 60*48))
    
    flag = random.choice(["Normal", "Normal", "Normal", "Abnormal", "Abnormal", "Critical"])
    status = random.choice(["Final", "Final", "Final", "Preliminary"])
    
    if order_type == "Lab":
        panel = random.choice(["Complete Blood Count", "Basic Metabolic Panel", "Comprehensive Metabolic Panel", "Hepatic Function Panel", "Troponin", "Arterial Blood Gas"])
        if panel == "Complete Blood Count":
            details = json.dumps({"WBC": round(random.uniform(4.0, 15.0), 1), "Hgb": round(random.uniform(7.0, 16.0), 1), "Plt": random.randint(50, 400)})
        else:
            details = json.dumps({"Sodium": random.randint(125, 145), "Potassium": round(random.uniform(3.0, 6.0), 1), "Creatinine": round(random.uniform(0.6, 3.5), 1)})
    elif order_type == "Imaging":
        panel = random.choice(["CT Head w/o Contrast", "Chest X-Ray AP", "MRI Brain", "Echocardiogram"])
        if flag == "Normal":
            details = "No acute findings. Unremarkable study."
        else:
            details = f"Abnormal findings noted in Region {random.randint(1,5)}. Please review PACS for full dictation."
    else:
        panel = "Blood Culture"
        details = "No growth at 24 hours." if flag == "Normal" else "Gram Positive Cocci in clusters."
        flag = "Normal" if flag == "Normal" else "Critical"

    cursor.execute('''
    INSERT INTO results (result_id, patient_id, order_type, panel_name, result_details, status, flag, result_time, routed_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"RES-{fake.random_int(min=1000000, max=9999999)}",
        pid,
        order_type,
        panel,
        details,
        status,
        flag,
        res_time.isoformat() + "Z",
        "DR-SMITH" # The active user
    ))

# ---------------------------------------------------------
# 4. Schedule & OR
# ---------------------------------------------------------
print("Creating 'schedule' table...")
cursor.execute('''
CREATE TABLE schedule (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT,
    event_type TEXT,
    location TEXT,
    provider TEXT,
    start_time TEXT,
    duration_mins INTEGER,
    status TEXT,
    notes TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
''')

print("Seeding OR Schedule & Clinics...")
base_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)

schedule_types = [
    {"type": "Surgery", "locations": ["OR-1", "OR-2", "OR-3", "Cath Lab"], "durations": [60, 120, 180, 240]},
    {"type": "Clinic", "locations": ["Cardiology Clinic", "Heart Failure Clinic", "General Surgery Clinic"], "durations": [15, 30, 45]}
]

for i in range(40):
    pid = random.choice(patient_ids)
    st_cat = random.choice(schedule_types)
    
    # Distribute events today and tomorrow
    day_offset = random.choice([0, 1])
    hour_offset = random.randint(0, 10)
    minute_offset = random.choice([0, 15, 30, 45])
    
    start_time = base_time + timedelta(days=day_offset, hours=hour_offset, minutes=minute_offset)
    
    status = random.choice(["Scheduled", "Arrived", "In Progress", "Completed", "Canceled"])
    
    cursor.execute('''
    INSERT INTO schedule (appointment_id, patient_id, event_type, location, provider, start_time, duration_mins, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"APP-{fake.random_int(min=100000, max=999999)}",
        pid,
        st_cat["type"],
        random.choice(st_cat["locations"]),
        "DR-SMITH", # The active user's schedule
        start_time.isoformat() + "Z",
        random.choice(st_cat["durations"]),
        status,
        f"Pre-op: cleared. Follow-up from {fake.date_this_year()}" if st_cat["type"] == "Surgery" else "Routine checkup."
    ))


# ---------------------------------------------------------
# 5. Provider Preferences
# ---------------------------------------------------------
print("Creating 'provider_preferences' table...")
cursor.execute('''
CREATE TABLE provider_preferences (
    provider_id TEXT PRIMARY KEY,
    theme TEXT,
    density TEXT,
    alert_threshold_hr INTEGER,
    session_timeout_minutes INTEGER
)
''')

print("Seeding default preferences for DR-SMITH...")
cursor.execute('''
INSERT INTO provider_preferences (provider_id, theme, density, alert_threshold_hr, session_timeout_minutes)
VALUES (?, ?, ?, ?, ?)
''', (
    "DR-SMITH",
    "system",
    "compact",
    100,
    15
))

# Create Indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_mpi_name ON patients (last_name, first_name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_mpi_mrn ON patients (mrn)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_encounters_unit ON encounters (unit)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_routed ON results (routed_to)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_status ON results (status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_provider ON schedule (provider)')

conn.commit()
conn.close()

print(f"Hospital Core Database generation complete! Data saved to: {DB_PATH}")
