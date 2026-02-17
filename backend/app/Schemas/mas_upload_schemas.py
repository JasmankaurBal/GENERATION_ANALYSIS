from pydantic import BaseModel
from typing import List, Dict, Any,Optional

class UploadResponse(BaseModel):
    success: bool
    message: str
    inserted: int
    failed: int
    errors: List[str] = []
    status:str
    rows_inserted:int
    duplicate_rows:int
    message:str


class FileUPloadResponse(BaseModel):
    file_id:int
    filename:str
    status:str
    rows_inserted:int
    error_log:Optional[str]
    class Config:
        from_attributes=True

class PreviewResponse(BaseModel):
    filename:str
    total_rows:int
    valid_rows:int
    invalid_rows:int
    duplicate_rows:int
    preview_data:List[Dict[str,Any]]
    message:str        