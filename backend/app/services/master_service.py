from sqlalchemy.orm import Session
from app.models.master_model import Plant, PlantType, Unit
from app.Schemas.master_schema import PlantCreate, UnitCreate


def create_plant(db: Session, plant: PlantCreate):

    # 🔥 AUTO GENERATE plant_code if missing
    plant_code = plant.plant_code if plant.plant_code else plant.plant_name


    db_plant = Plant(

        plant_code=plant_code,

        plant_name=plant.plant_name,

        type_id=plant.type_id,

        location=plant.location,

        district=plant.district,

        state=plant.state,

        commissioning_date=plant.commissioning_date,

        retirement_date=plant.retirement_date,

        status=plant.status,

        installed_capacity_mw=plant.installed_capacity_mw,

        implementing_agency=plant.implementing_agency,

        sector=plant.sector

    )

    db.add(db_plant)

    db.commit()

    db.refresh(db_plant)

    return {
        "success": True,
        "message": "Plant created successfully",
        "plant_id": db_plant.plant_id
    }



def create_unit(db: Session, unit: UnitCreate):

    db_unit = Unit(

        plant_id=unit.plant_id,

        unit_code=unit.unit_code,

        unit_capacity_mw=unit.unit_capacity_mw,

        commissioning_date=unit.commissioning_date,

        status=unit.status

    )

    db.add(db_unit)

    db.commit()

    db.refresh(db_unit)

    return {

        "success": True,

        "message": "Unit created successfully",

        "unit_id": db_unit.unit_id

    }
def get_plant_types(db: Session):

    return db.query(PlantType).all()

def get_plants(db: Session):

    return db.query(Plant).all()

def get_units(db: Session):

    return db.query(Unit).all()

