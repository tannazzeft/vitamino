# ------------------------------
# supplement-checker/backend/main.py
# ------------------------------

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
from typing import List
from fuzzywuzzy import fuzz
import re

app = FastAPI()

# CORS (برای اینکه Streamlit یا Frontend به این API وصل شه)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در حالت واقعی فقط دامنهٔ خودت باشه
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalize(text):
    text = str(text).strip().lower().replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"[^\w\s]", "", text)

def load_data():
    conn = sqlite3.connect("backend/db/output(2)(1).sqlite")
    df_disease = pd.read_sql_query("SELECT * FROM Sheet4", conn)
    df_drug = pd.read_sql_query("SELECT * FROM Sheet3", conn)
    df_preg = pd.read_sql_query("SELECT * FROM Sheet2", conn)
    conn.close()
    return df_disease, df_drug, df_preg

df_disease, df_drug, df_preg = load_data()

@app.get("/")
def root():
    return {"message": "✅ Supplement Interaction API is running"}

@app.get("/interactions")
def get_interactions(
    supplement: str = Query(...),
    drugs: List[str] = Query([]),
    diseases: List[str] = Query([])
):
    supp_norm = normalize(supplement)
    drug_results, disease_results = [], []

    for _, row in df_drug.iterrows():
        if fuzz.partial_ratio(normalize(row["ماده فعال / Compound"]), supp_norm) > 85:
            for d in drugs:
                if fuzz.partial_ratio(normalize(row["داروی درگیر / Interacting Drug"]), normalize(d)) > 85:
                    drug_results.append({
                        "compound": row["ماده فعال / Compound"],
                        "drug": row["داروی درگیر / Interacting Drug"],
                        "severity": row["شدت / Severity (A–X)"],
                        "advice": row["توصیه بالینی / Clinical Advice"]
                    })

    for _, row in df_disease.iterrows():
        if fuzz.partial_ratio(normalize(row["ماده فعال / Compound"]), supp_norm) > 85:
            for dis in diseases:
                if fuzz.partial_ratio(normalize(row["بیماری / Condition"]), normalize(dis)) > 85:
                    disease_results.append({
                        "compound": row["ماده فعال / Compound"],
                        "condition": row["بیماری / Condition"],
                        "severity": row["شدت تداخل (A–X) / Severity"],
                        "advice": row["توصیه بالینی / Clinical Advice"]
                    })

    return {
        "supplement": supplement,
        "drug_interactions": drug_results,
        "disease_interactions": disease_results
    }
