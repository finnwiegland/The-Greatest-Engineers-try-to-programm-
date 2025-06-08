from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SensorModel(BaseModel):
    id: str
    name: str
    type: str
    building_id: str
    floor: int
    room: int


class SensorReading(BaseModel):
    type: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[datetime] = None
