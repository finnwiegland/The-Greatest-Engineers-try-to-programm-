from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from models import SensorData, BIMModelMetadata
from database import db
import os
import shutil

app = FastAPI()

bim_collection = db["bim_models"]
sensor_collection = db["sensor_data"]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ───────── BIM MODELLE ─────────

@app.post("/bim/upload")
async def upload_bim_model(file: UploadFile = File(...), meta: str = ""):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    metadata = {"filename": file.filename, "path": path, "meta": meta}
    bim_collection.insert_one(metadata)
    return {"message": "BIM-Modell hochgeladen", "filename": file.filename}

@app.get("/bim/list")
def list_bim_models():
    return [{"id": str(doc["_id"]), "filename": doc["filename"], "meta": doc.get("meta", "")}
            for doc in bim_collection.find()]

@app.get("/bim/download/{filename}")
def download_bim_model(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    return FileResponse(path, media_type='application/octet-stream', filename=filename)

# ───────── SENSOR DATEN ─────────

@app.post("/sensors")
def add_sensor_data(data: SensorData):
    result = sensor_collection.insert_one(data.dict())
    return {"message": "Sensordaten gespeichert", "id": str(result.inserted_id)}

@app.get("/sensors")
def get_all_sensor_data():
    data = []
    for doc in sensor_collection.find():
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        data.append(doc)
    return data
