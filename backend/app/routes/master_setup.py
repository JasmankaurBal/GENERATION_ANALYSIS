from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.Schemas.master_schema import (
    PlantCreate,
    PlantTypeResponse, 
    UnitCreate,
PlantResponse,  PlantTypeResponse )

from app.services.master_service import (
     create_plant,
     create_unit,
     get_plants,
        get_units,
        get_plant_types
)

router = APIRouter(
    prefix="/master",
    tags=["Master Setup"]
)
 


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



@router.post("/plant")

def add_plant(

    plant: PlantCreate,

    db: Session = Depends(get_db)

):

    return create_plant(db, plant)



@router.post("/unit")

def add_unit(

    unit: UnitCreate,

    db: Session = Depends(get_db)

):

    return create_unit(db, unit)
@router.get("/plants", response_model=List[PlantResponse])
def list_plants(db: Session = Depends(get_db)):

    return get_plants(db)

@router.get("/units")
def list_units(db: Session = Depends(get_db)):

    return get_units(db)

@router.get("/plant-types", response_model=List[PlantTypeResponse])
def list_plant_types(db: Session = Depends(get_db)):
    return get_plant_types(db)

