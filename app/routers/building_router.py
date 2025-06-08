from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, StreamingResponse

from app.models.building_model import BuildingModel as Building
from app.util import mongo_db_connector

import os

from pymongo import MongoClient
import gridfs
import app.config as config

router = APIRouter(prefix="/buildings", tags=["buildings"])
templates = Jinja2Templates(directory="app/templates")

# 1. Endpoints for frontend tempaltes rendering


@router.get("/management")
async def building_management(request: Request):
    buildings = await get_buildings()
    return templates.TemplateResponse("buildings.html", {"request": request, "buildings": buildings})

# 2. Endpoints for general operations on ALL buildings


@router.get("/")
async def read_buildings():
    """Fetches all buildings from the database."""
    buildings = await get_buildings()
    return buildings


@router.post("/")
async def create_building(building_data: Building):
    """Creates a new building and stores it in the database."""
    buildings_collection = mongo_db_connector.init_db("buildings")
    buildings_collection.insert_one(building_data.model_dump())
    return {"message": "Building added successfully", "building": building_data}

# 3. Endpoints for operations on a specific building


@router.get("/{building_id}")
async def read_building(building_id: str):
    """Fetches specific building from the database by building_id."""
    buildings = await get_buildings(id=building_id)
    if not buildings:
        raise HTTPException(status_code=404, detail="Building not found")
    return buildings[0]


@router.put("/{building_id}")
async def update_building(building_id: str, building_data: Building):
    """Updates a specific building in the database."""
    buildings_collection = mongo_db_connector.init_db("buildings")
    buildings_collection.update_one({"id": building_id}, {
                                    "$set": building_data.model_dump()})
    return {"message": "Building updated successfully", "building": building_data}


@router.delete("/{building_id}")
async def delete_building(building_id: str):
    """Deletes a specific building from the database."""
    buildings_collection = mongo_db_connector.init_db("buildings")
    result = buildings_collection.delete_one({"id": building_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"message": "Building deleted successfully", "building_id": building_id}

# 4. Endpoints for specific operations on buildings (IFC file upload, sensors, etc.)


@router.get("/{building_id}/sensors")
async def get_building_sensors(building_id: str):
    """Returns sensors for a specific building."""
    sensors_collection = mongo_db_connector.init_db("sensors")
    sensors = list(sensors_collection.find({"building_id": building_id}))
    for s in sensors:
        s.pop("_id", None)
    return sensors


@router.get("/{building_id}/dashboard-data")
async def building_dashboard_data(building_id: str):
    """Generates a dashboard (JSON format) for a specific building --> no. of sensors, sensor types, etc."""
    sensors_collection = mongo_db_connector.init_db("sensors")
    sensors = list(sensors_collection.find({"building_id": building_id}))
    for sensor in sensors:
        sensor.pop("_id", None)
    return {
        "building_id": building_id,
        "total_sensors": len(sensors),
        "sensors": sensors
    }


@router.post("/{building_id}/upload_ifc")
async def upload_ifc_file(building_id: str, file: UploadFile = File(...)):
    """Uploads an IFC file for a specific building using GridFS."""

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="File must be an IFC file")

    client = MongoClient(config.MONGO_ADDRESS)
    db = client[config.MONGO_DB_NAME]
    fs = gridfs.GridFS(db, collection="ifc_files")

    content = await file.read()
    file_id = fs.put(
        content, filename=f"{building_id}.ifc", building_id=building_id)

    return {"message": "IFC file uploaded successfully", "file_id": str(file_id)}


@router.get("/{building_id}/ifc_file")
async def get_ifc_file(building_id: str):
    """Fetches IFC file for a specific building."""
    client = MongoClient(config.MONGO_ADDRESS)
    db = client[config.MONGO_DB_NAME]
    fs = gridfs.GridFS(db, collection="ifc_files")

    grid_out = fs.find_one({"building_id": building_id})
    if not grid_out:
        raise HTTPException(
            status_code=404, detail="IFC file not found for this building")

    return StreamingResponse(
        grid_out,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={grid_out.filename}"}
    )


@router.get("/{building_id}/dashboard")
async def building_dashboard(request: Request, building_id: str):
    """Renders a dashboard (visual) for a specific building."""
    buildings = await get_buildings(id=building_id)
    if not buildings:
        raise HTTPException(status_code=404, detail="Building not found")
    building = buildings[0]

    sensors_collection = mongo_db_connector.init_db("sensors")
    sensors = list(sensors_collection.find({"building_id": building_id}))
    for sensor in sensors:
        sensor.pop("_id", None)

    return templates.TemplateResponse("building_dashboard.html", {
        "request": request,
        "building": building,
        "sensors": sensors,
        "building_id": building_id
    })


async def get_buildings(name: str = None, project: str = None, location: str = None, id: str = None) -> list:
    """Fetches buildings from the database depending on received params."""
    buildings_collection = mongo_db_connector.init_db("buildings")
    query = {}
    if name:
        query["name"] = name
    if project:
        query["project"] = project
    if location:
        query["location"] = location
    if id:
        query["id"] = id
    buildings = buildings_collection.find(query)
    buildings_return = []
    for building in buildings:
        building.pop("_id", None)
        buildings_return.append(building)
    return buildings_return
