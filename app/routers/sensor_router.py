from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

from app.models.sensor_model import SensorModel as Sensor
from app.models.sensor_model import SensorReading
from app.util import mongo_db_connector

from datetime import datetime

router = APIRouter(prefix="/sensors", tags=["sensors"])
templates = Jinja2Templates(directory="templates")


@router.get("/management")
async def sensor_management(request: Request):
    """ Render the sensor management page. """
    db = mongo_db_connector.init_db("sensors")
    sensors = list(db.find({}))
    for s in sensors:
        s.pop("_id", None)
    return templates.TemplateResponse("sensors.html", {"request": request, "sensors": sensors})


@router.get("/")
async def get_sensors(building_id: str = None):
    """ Get all sensors or sensors for a specific building. """
    db = mongo_db_connector.init_db("sensors")
    query = {"building_id": building_id} if building_id else {}
    sensors = list(db.find(query))
    for s in sensors:
        s.pop("_id", None)
    return sensors


@router.post("/")
async def create_sensor(sensor: Sensor):
    """ Create a new sensor and store it in the database. """
    db = mongo_db_connector.init_db("sensors")
    db.insert_one(sensor.model_dump())
    return {"message": "Sensor created successfully", "sensor_id": sensor.id}


@router.get("/create")
async def create_sensor_form(request: Request):
    """ Render form (HTML) to create a new sensor. """
    return templates.TemplateResponse("create_sensor.html", {"request": request})


@router.get("/{sensor_id}")
async def read_sensor(sensor_id: str):
    """ Gets data from a specific sensor by its ID. """
    db = mongo_db_connector.init_db("sensors")
    sensor = db.find_one({"id": sensor_id})
    if sensor:
        sensor.pop("_id", None)
        return sensor
    raise HTTPException(status_code=404, detail="Sensor not found")


@router.put("/{sensor_id}")
async def update_sensor(sensor_id: str, sensor: Sensor):
    """ Update an existing sensor's data. """
    db = mongo_db_connector.init_db("sensors")
    result = db.update_one({"id": sensor_id}, {"$set": sensor.model_dump()})
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="Sensor not found or no changes made")
    return {"message": "Sensor updated successfully", "sensor_id": sensor_id}


@router.delete("/{sensor_id}")
async def delete_sensor(sensor_id: str):
    """ Delete a sensor from database by its ID. """
    db = mongo_db_connector.init_db("sensors")
    result = db.delete_one({"id": sensor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return {"message": "Sensor deleted successfully", "sensor_id": sensor_id}


@router.get("/type/{type}")
async def get_sensors_by_type(type: str):
    """ Returns sensors of a specific type. """
    db = mongo_db_connector.init_db("sensors")
    sensors = list(db.find({"type": type}))
    for s in sensors:
        s.pop("_id", None)
    return sensors


@router.post("/{sensor_id}/value")
async def update_sensor_value(sensor_id: str, reading: SensorReading):
    """ Create a new sensor reading and store it in the database. """
    db = mongo_db_connector.init_db("sensor_readings")
    reading_data = reading.model_dump()
    reading_data["sensor_id"] = sensor_id
    reading_data["timestamp"] = datetime.now()
    db.insert_one(reading_data)
    return {"message": "Sensor reading created successfully", "reading_id": reading_data.get("id")}


@router.get("/readings/{sensor_id}")
async def get_sensor_readings(sensor_id: str):
    """ Get all readings for a specific sensor. """
    db = mongo_db_connector.init_db("sensor_readings")
    readings = list(db.find({"sensor_id": sensor_id}))

    if not readings:
        raise HTTPException(
            status_code=404, detail="No readings found for this sensor")

    for reading in readings:
        reading.pop("_id", None)
        if "timestamp" in reading and reading["timestamp"]:
            reading["timestamp"] = reading["timestamp"].isoformat()

    return readings
