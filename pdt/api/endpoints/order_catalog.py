from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import sqlite3
import os
import json
from pydantic import BaseModel

router = APIRouter()

# Define Paths
# __file__ is /Users/pratikkumar/Desktop/Human Digit Twin/pdt/api/endpoints/order_catalog.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "order_catalog.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Order Catalog Database not found. Please run seed script.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Response Models
class CatalogCategory(BaseModel):
    id: str
    name: str

class CatalogItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: str # med, lab, imaging, set
    details: Optional[dict] = None # For extra fields like composition or price

@router.get("/categories", response_model=List[CatalogCategory])
async def get_categories():
    """Returns the primary tabs for the Orders Board Catalog."""
    return [
        {"id": "sets", "name": "Order Sets"},
        {"id": "meds", "name": "Medications"},
        {"id": "labs", "name": "Laboratory"},
        {"id": "imaging", "name": "Imaging"}
    ]

@router.get("/items", response_model=List[CatalogItem])
async def get_catalog_items(
    category: str = Query(..., description="Category: sets, meds, labs, imaging"),
    search: Optional[str] = Query(None, description="Search term for names or active ingredients")
):
    """
    Returns items for a specific catalog category.
    Includes a robust search to handle filtering 250k+ medications by brand or composition.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    items = []

    try:
        if category == "meds":
            # Search limit to 100 for performance on the dense UI
            if search:
                query = f"%{search}%"
                cursor.execute("""
                    SELECT id, name, type, short_composition1, short_composition2, price_inr, manufacturer_name
                    FROM medications
                    WHERE name LIKE ? 
                       OR short_composition1 LIKE ? 
                       OR short_composition2 LIKE ?
                    LIMIT 200
                """, (query, query, query))
            else:
                cursor.execute("""
                    SELECT id, name, type, short_composition1, short_composition2, price_inr, manufacturer_name
                    FROM medications
                    LIMIT 200
                """)
                
            for row in cursor.fetchall():
                comp1 = row["short_composition1"] if row["short_composition1"] else ""
                comp2 = row["short_composition2"] if row["short_composition2"] else ""
                desc = f"{comp1} {comp2}".strip()
                
                details = {
                    "price_inr": row["price_inr"],
                    "manufacturer": row["manufacturer_name"]
                }
                
                items.append({
                    "id": str(row["id"]),
                    "name": row["name"],
                    "description": desc if desc else "Composition not specified",
                    "type": "med",
                    "details": details
                })
                
        elif category == "labs":
            if search:
                cursor.execute("SELECT * FROM labs WHERE name LIKE ? OR panel LIKE ?", (f"%{search}%", f"%{search}%"))
            else:
                cursor.execute("SELECT * FROM labs")
                
            for row in cursor.fetchall():
                items.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": f"{row['panel']} • LOINC: {row['loinc_code']}\n{row['description']}",
                    "type": "lab"
                })

        elif category == "imaging":
            if search:
                cursor.execute("SELECT * FROM imaging WHERE name LIKE ? OR modality LIKE ?", (f"%{search}%", f"%{search}%"))
            else:
                cursor.execute("SELECT * FROM imaging")
                
            for row in cursor.fetchall():
                items.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": f"{row['modality']} • {row['body_part']}\n{row['description']}",
                    "type": "imaging"
                })

        elif category == "sets":
            if search:
                cursor.execute("SELECT * FROM order_sets WHERE name LIKE ? OR specialty LIKE ?", (f"%{search}%", f"%{search}%"))
            else:
                cursor.execute("SELECT * FROM order_sets")
                
            for row in cursor.fetchall():
                items.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": f"{row['specialty']}: {row['description']}",
                    "type": "set",
                    "details": {"components": json.loads(row["components_json"])}
                })
        else:
            raise HTTPException(status_code=400, detail="Invalid category")

    except Exception as e:
        print(f"Error fetching catalog items: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        conn.close()

    return items

class OrderSubmission(BaseModel):
    patient_id: str
    items: List[dict]
    provider_id: str

@router.post("/submit")
async def submit_orders(order: OrderSubmission):
    """
    Mock endpoint to receive the Scratchpad "Sign & Submit" action from the CPOE frontend.
    """
    total_items = len(order.items)
    print(f"Received {total_items} orders for Patient {order.patient_id} directly from {order.provider_id}")
    
    # In a real system, we'd insert these into a patient's active orders table.
    return {
        "status": "success",
        "message": f"Successfully signed and routed {total_items} orders to the hospital network."
    }
