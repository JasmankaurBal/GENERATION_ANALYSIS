from sqlalchemy import Column, TIMESTAMP,Integer,Text, String, Date, Enum, ForeignKey, DECIMAL ,Boolean
from app.core.database import Base
import enum


class PlantStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class Plant(Base):

    __tablename__ = "plant_master"

    plant_id = Column(Integer, primary_key=True, index=True)

    plant_code = Column(String(50), unique=True, nullable=False)

    plant_name = Column(String(100), nullable=False)

    type_id =Column(Integer, ForeignKey("plant_type_master.type_id"))

    location = Column(String(100))

    district = Column(String(50))

    state = Column(String(50))

    commissioning_date = Column(Date)

    retirement_date = Column(Date)

    status = Column(Enum(PlantStatus))

    installed_capacity_mw = Column(DECIMAL(10,2))

    implementing_agency = Column(String(100)) 
    sector = Column(String(50))

class UnitStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"


class Unit(Base):

    __tablename__ = "unit_master"

    unit_id = Column(Integer, primary_key=True)

    plant_id = Column(Integer, ForeignKey("plant_master.plant_id"))

    unit_code = Column(String(50))

    unit_capacity_mw = Column(DECIMAL(10,2))

    commissioning_date = Column(Date)

    status = Column(Enum(UnitStatus))


class PlantType(Base):
    __tablename__ = "plant_type_master"

    type_id = Column(Integer, primary_key=True, index=True)

    power_source = Column(String(50), nullable=False)
    fuel_type = Column(String(50))
    is_renewable = Column(Integer) 

class PlantStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class UploadStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class FileIngestionLog(Base):
    __tablename__= "file_ingestion_log"

    file_id=Column(Integer,primary_key=True , index=True ,autoincrement=True)    
    filename=Column( String(255), nullable=False)
    storage_path=Column(String(512))
    file_size_kb=Column(Integer)
    rows_inserted=Column(Integer ,default=0)
    status=Column(Enum(UploadStatus), default=UploadStatus.PROCESSING)
    data_category=Column(String(100))
    error_log=Column(Text)
    uploaded_by=Column(String(100))
    uploaded_at=Column(TIMESTAMP)