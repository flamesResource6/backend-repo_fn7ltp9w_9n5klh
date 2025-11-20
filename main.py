import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from schemas import Lead

app = FastAPI(title="Meri Skin Perfect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Meri Skin Perfect API running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Lead capture endpoint
@app.post("/api/leads")
def create_lead(lead: Lead) -> Dict[str, Any]:
    """Store a lead for the First Diagnostic Consultation"""
    try:
        from database import create_document
        inserted_id = create_document("lead", lead)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple content endpoints for the frontend
@app.get("/api/testimonials")
def get_testimonials():
    return [
        {
            "name": "Giulia, 27",
            "text": "Dopo il metodo Zero Brufoli la mia pelle è finalmente pulita. Niente più fondotinta pesante!",
        },
        {
            "name": "Francesca, 41",
            "text": "Zero Rughe mi ha ridato tonicità senza aghi. Meri è una professionista impeccabile.",
        },
        {
            "name": "Sara, 33",
            "text": "Diagnosi con microcamera super precisa. Piano personalizzato e risultati visibili in 6 settimane.",
        },
    ]

@app.get("/api/before-after")
def get_before_after():
    # Placeholder image URLs; in production serve from a CDN or storage
    return [
        {"before": "/ba/before1.jpg", "after": "/ba/after1.jpg"},
        {"before": "/ba/before2.jpg", "after": "/ba/after2.jpg"},
        {"before": "/ba/before3.jpg", "after": "/ba/after3.jpg"},
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
