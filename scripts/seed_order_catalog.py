import sqlite3
import pandas as pd
import os
import json

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(BASE_DIR, "A_Z_medicines_dataset_of_India.csv")
DB_PATH = os.path.join(DATA_DIR, "order_catalog.db")

print(f"Creating Order Catalog Database at: {DB_PATH}")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Remove old DB if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Create Medications Table
print("Creating 'medications' table...")
cursor.execute('''
CREATE TABLE medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    manufacturer_name TEXT,
    price_inr REAL,
    is_discontinued BOOLEAN,
    type TEXT,
    pack_size_label TEXT,
    short_composition1 TEXT,
    short_composition2 TEXT
)
''')

# Load and Insert CSV Data
print(f"Reading CSV from: {CSV_PATH}")
# Use chunking as it's a very large file (~250k rows)
chunk_size = 50000
total_processed = 0

try:
    for chunk in pd.read_csv(CSV_PATH, chunksize=chunk_size, low_memory=False):
        # Rename columns to match SQLite schema
        chunk = chunk.rename(columns={
            'price(₹)': 'price_inr',
            'Is_discontinued': 'is_discontinued'
        })
        
        # Drop the original CSV 'id' if it exists to let SQLite auto-increment cleanly
        if 'id' in chunk.columns:
            chunk = chunk.drop(columns=['id'])

        # Write to SQLite
        chunk.to_sql('medications', conn, if_exists='append', index=False)
        total_processed += len(chunk)
        print(f"Inserted {total_processed} medication records...")
        
    print(f"Successfully loaded {total_processed} medications into the database.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    # We will generate mock data if CSV fails
    print("Falling back to mock Indian medications...")
    
    mock_meds = [
         ('Crocin 500mg', 'GSK', 15.0, False, 'allopathy', '15 tablets', 'Paracetamol (500mg)', ''),
         ('Dolo 650', 'Micro Labs', 30.0, False, 'allopathy', '15 tablets', 'Paracetamol (650mg)', ''),
         ('Shelcal 500', 'Torrent', 120.0, False, 'allopathy', '15 tablets', 'Calcium (500mg)', 'Vitamin D3 (250 IU)'),
         ('Augmentin 625 Duo', 'GSK', 223.0, False, 'allopathy', '10 tablets', 'Amoxycillin (500mg)', 'Clavulanic Acid (125mg)'),
         ('Pan 40', 'Alkem', 150.0, False, 'allopathy', '15 tablets', 'Pantoprazole (40mg)', ''),
         ('O2 Tablet', 'Medley', 160.0, False, 'allopathy', '10 tablets', 'Ofloxacin (200mg)', 'Ornidazole (500mg)'),
         ('Azee 500', 'Cipla', 132.0, False, 'allopathy', '5 tablets', 'Azithromycin (500mg)', '')
    ]
    cursor.executemany('''
    INSERT INTO medications (name, manufacturer_name, price_inr, is_discontinued, type, pack_size_label, short_composition1, short_composition2)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', mock_meds)


# 2. Create Labs Table
print("Creating 'labs' table...")
cursor.execute('''
CREATE TABLE labs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    panel TEXT,
    loinc_code TEXT,
    description TEXT
)
''')

mock_labs = [
    ('LAB-001', 'Complete Blood Count (CBC)', 'Hematology', '58410-5', 'Evaluates overall health and detects a wide range of disorders, including anemia, infection and leukemia.'),
    ('LAB-002', 'Basic Metabolic Panel (BMP)', 'Chemistry', '24320-4', 'Measures your sugar (glucose) level, electrolyte and fluid balance, and kidney function.'),
    ('LAB-003', 'Comprehensive Metabolic Panel (CMP)', 'Chemistry', '24323-8', 'Includes BMP plus liver function tests.'),
    ('LAB-004', 'Lipid Panel', 'Cardiology', '24331-1', 'Measures cholesterol and triglyceride levels to assess heart disease risk.'),
    ('LAB-005', 'Hemoglobin A1C', 'Endocrinology', '4548-4', 'Measures average blood sugar concentration over the past two to three months.'),
    ('LAB-006', 'Thyroid Stimulating Hormone (TSH)', 'Endocrinology', '3016-3', 'Evaluates thyroid function.'),
    ('LAB-007', 'Prothrombin Time (PT/INR)', 'Coagulation', '5902-2', 'Evaluates blood clotting.'),
    ('LAB-008', 'Urinalysis', 'Nephrology', '24356-8', 'Screens for a variety of conditions, such as urinary tract infections, kidney disease and diabetes.'),
    ('LAB-009', 'Troponin', 'Cardiology', '6598-7', 'Measures troponin levels to diagnose heart attacks.')
]
cursor.executemany('INSERT INTO labs (id, name, panel, loinc_code, description) VALUES (?, ?, ?, ?, ?)', mock_labs)


# 3. Create Imaging Table
print("Creating 'imaging' table...")
cursor.execute('''
CREATE TABLE imaging (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    modality TEXT,
    body_part TEXT,
    description TEXT
)
''')

mock_imaging = [
    ('IMG-001', 'Chest X-Ray (PA & Lateral)', 'X-Ray', 'Chest', 'Standard 2-view evaluation of lungs, heart, and chest wall.'),
    ('IMG-002', 'CT Head without Contrast', 'CT', 'Head', 'Evaluates for acute hemorrhage, stroke, or mass.'),
    ('IMG-003', 'MRI Brain with Contrast', 'MRI', 'Brain', 'Detailed evaluation of brain parenchyma for tumors, infection, or MS.'),
    ('IMG-004', 'Ultrasound Abdomen Complete', 'Ultrasound', 'Abdomen', 'Evaluates liver, gallbladder, kidneys, spleen, and pancreas.'),
    ('IMG-005', 'Echocardiogram Transthoracic', 'Echocardiography', 'Heart', 'Evaluates cardiac chambers, valves, and overall pumping function.'),
    ('IMG-006', 'CT Chest/Abdomen/Pelvis w/ Contrast', 'CT', 'Torso', 'Comprehensive evaluation for trauma, oncology staging, or acute abdominal pain.'),
    ('IMG-007', 'X-Ray Knee (AP, Lateral, Sunrise)', 'X-Ray', 'Knee', 'Evaluates for fractures, osteoarthritis, or joint effusion.'),
    ('IMG-008', 'DEXA Bone Density Scan', 'DEXA', 'Full Body', 'Measures bone mineral density to screen for osteoporosis.')
]
cursor.executemany('INSERT INTO imaging (id, name, modality, body_part, description) VALUES (?, ?, ?, ?, ?)', mock_imaging)


# 4. Create Order Sets Table
print("Creating 'order_sets' table...")
cursor.execute('''
CREATE TABLE order_sets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    specialty TEXT,
    description TEXT,
    components_json TEXT
)
''')

# Store components as JSON arrays referencing other tables
mock_order_sets = [
    (
        'OS-001', 
        'Adult Sepsis Protocol (3-Hour Bundle)', 
        'Emergency / ICU', 
        'Standard initial pathway for suspected sepsis or septic shock.',
        json.dumps([
            {"type": "lab", "id": "LAB-001", "name": "Complete Blood Count (CBC)"},
            {"type": "lab", "id": "LAB-003", "name": "Comprehensive Metabolic Panel (CMP)"},
            {"type": "imaging", "id": "IMG-001", "name": "Chest X-Ray (PA & Lateral)"},
            {"type": "med", "name": "Normal Saline 0.9% IV 30cc/kg", "desc": "Fluid Resuscitation"},
            {"type": "med", "name": "Vancomycin IV", "desc": "Broad-spectrum coverage (MRSA)"},
            {"type": "med", "name": "Cefepime IV", "desc": "Broad-spectrum coverage (Pseudomonas)"}
        ])
    ),
    (
        'OS-002', 
        'Acute Myocardial Infarction (STEMI)', 
        'Cardiology', 
        'Immediate orders for acute coronary syndrome.',
        json.dumps([
            {"type": "lab", "id": "LAB-009", "name": "Troponin"},
            {"type": "lab", "id": "LAB-002", "name": "Basic Metabolic Panel (BMP)"},
            {"type": "lab", "id": "LAB-007", "name": "Prothrombin Time (PT/INR)"},
            {"type": "imaging", "id": "IMG-001", "name": "Chest X-Ray (Portable)"},
            {"type": "med", "name": "Aspirin 325mg PO", "desc": "Antiplatelet"},
            {"type": "med", "name": "Clopidogrel 600mg PO", "desc": "P2Y12 inhibitor load"},
            {"type": "med", "name": "Atorvastatin 80mg PO", "desc": "High-intensity statin"}
        ])
    ),
    (
        'OS-003',
        'Diabetes Ketoacidosis (DKA) Protocol',
        'Endocrinology / ICU',
        'Initial management pathway for severe hyperglycemia and acidosis.',
        json.dumps([
             {"type": "lab", "id": "LAB-002", "name": "Basic Metabolic Panel (BMP)"},
             {"type": "lab", "id": "LAB-005", "name": "Hemoglobin A1C"},
             {"type": "lab", "id": "LAB-008", "name": "Urinalysis"},
             {"type": "med", "name": "Regular Insulin IV Drip", "desc": "0.1 units/kg/hr"},
             {"type": "med", "name": "Normal Saline 0.9% IV 1000ml", "desc": "Bolus for hydration"},
             {"type": "med", "name": "Potassium Chloride IV", "desc": "Replenish intracellular K+"}
        ])
    )
]
cursor.executemany('INSERT INTO order_sets (id, name, specialty, description, components_json) VALUES (?, ?, ?, ?, ?)', mock_order_sets)


# Add Text Indexes for faster Medication searching
print("Creating indexes on medications for faster searching...")
cursor.execute('CREATE INDEX IF NOT EXISTS idx_med_name ON medications (name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_med_comp1 ON medications (short_composition1)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_med_comp2 ON medications (short_composition2)')

conn.commit()
conn.close()

print(f"Catalog DB generation complete! Data saved to: {DB_PATH}")
