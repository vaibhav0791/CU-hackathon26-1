import sqlite3
import json
from datetime import datetime
from bson import ObjectId

# Load drugs from JSON
with open('drugs.json', 'r') as f:
    drugs = json.load(f)

conn = sqlite3.connect("pharma.db")
cursor = conn.cursor()

for drug in drugs:
    _id = str(ObjectId())
    timestamp = datetime.utcnow().isoformat()
    
    cursor.execute('''
        INSERT INTO analysis_blueprint 
        (_id, drug_name, smiles, bcs_class, solubility_score, confidence_score, molecular_weight, timestamp, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        _id, 
        drug['drug_name'], 
        drug['smiles'], 
        drug['bcs_class'], 
        75.0,
        85.0,
        None,
        timestamp, 
        timestamp, 
        timestamp
    ))

conn.commit()
print("✅ All drugs seeded from drugs.json!")
conn.close()