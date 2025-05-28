from pydantic import BaseModel
from typing import Optional

class SensorData(BaseModel):
    sensor_id: str
    type: str  # z.B. "temperature", "humidity"
    value: float
    unit: str
    timestamp: Optional[str]  # ISO-Format optional

class BIMModelMetadata(BaseModel):
    name: str
    description: Optional[str]
