from fastapi import FastAPI
from app.core.database import Base, engine
from app.routes import master_setup
from fastapi.middleware.cors import CORSMiddleware
from app.models.master_model import Plant, Unit, PlantType
from app.routes import mas_upload
app = FastAPI()

Base.metadata.create_all(bind=engine)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "127.0.0.1:3000"],  # React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(master_setup.router)
app.include_router(mas_upload.router)