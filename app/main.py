from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers.building_router import router as building_router
from app.routers.sensor_router import router as sensor_router

app = FastAPI()

app.include_router(building_router)
app.include_router(sensor_router)


@app.get("/")
def read_root():
    return RedirectResponse("/buildings/management", status_code=303)
