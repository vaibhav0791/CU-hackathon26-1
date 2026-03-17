from pydantic import BaseModel

class ExportMetadata(BaseModel):
    filename: str
    file_format: str
    export_time: str
    total_records: int

class CSVExport(BaseModel):
    metadata: ExportMetadata
    data: list[list[str]]  # List of records, each record is a list of values

class JSONExport(BaseModel):
    metadata: ExportMetadata
    data: list[dict]  # List of records, each record is a dictionary
