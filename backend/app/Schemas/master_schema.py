from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional


class PlantCreate(BaseModel):

    # optional now
    plant_code: Optional[str] = None

    # required
    plant_name: str

    # required
    type_id: int

    # required
    state: str

    # required
    district: str

    # optional
    location: Optional[str] = None

    commissioning_date: Optional[date] = None

    retirement_date: Optional[date] = None

    installed_capacity_mw: Optional[Decimal] = None

    implementing_agency: Optional[str] = None

    sector: Optional[str] = None

    # required
    status: str



class UnitCreate(BaseModel):

    plant_id: int

    unit_code: str

    unit_capacity_mw: Decimal

    commissioning_date: date

    status: str

class PlantTypeResponse(BaseModel):

    type_id: int

    power_source: str

    fuel_type: Optional[str] = None

    is_renewable: Optional[int] = None

    class Config:
        from_attributes = True


class PlantResponse(BaseModel):     
    plant_id: int
    plant_name: str
    plant_code: Optional[str] 
    class Config:
        from_attributes = True   
