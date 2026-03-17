from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum

class RequestType(str, Enum):
    ANALYZE = "analyze"
    FETCH_DRUG = "fetch_drug"
    GET_MOLECULE_3D = "get_molecule_3d"
    COMPARE = "compare"
    WHAT_IF = "what_if"
    OTHER = "other"

class APIAnalytics(Document):
    """✅ V-5: Track all API requests and performance metrics"""
    
    # Request info
    request_id: str
    request_type: RequestType
    endpoint: str
    
    # Request data
    drug_name: Optional[str] = None
    smiles: Optional[str] = None
    
    # Performance metrics
    response_time_ms: float  # milliseconds
    status_code: int
    is_error: bool = False
    error_message: Optional[str] = None
    
    # Cache info
    was_cached: bool = False
    cache_hit: bool = False
    
    # Timestamp
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "api_analytics"

class AnalyticsSummary(Document):
    """✅ V-5: Summary statistics (updated daily)"""
    
    date: str  # YYYY-MM-DD format
    
    # Counts
    total_requests: int = 0
    total_errors: int = 0
    total_cache_hits: int = 0
    
    # Performance
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    
    # Popular drugs
    most_analyzed_drugs: dict = {}  # {"drug_name": count}
    
    # Cache stats
    cache_hit_rate: float = 0.0
    
    # Endpoints
    endpoint_stats: dict = {}  # {"endpoint": count}
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "analytics_summary"