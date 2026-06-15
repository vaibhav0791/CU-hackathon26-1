from pydantic import BaseModel, Field, ConfigDict

class Document(BaseModel):
    pass

ASCENDING = 1

from datetime import datetime
from typing import Optional
from enum import Enum

# ✅ Request Type Enum
class RequestType(str, Enum):
    ANALYZE = "analyze"
    FETCH_DRUG = "fetch_drug"
    GET_MOLECULE_3D = "get_molecule_3d"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    EXPORT_DATA = "export_data"

# ✅ API Analytics Data Model
class APIAnalytics(Document):
    """✅ API Request Analytics - MongoDB Document"""
    
    # Request tracking
    request_id: str = Field(..., description="Unique request identifier")
    request_type: str = Field(..., description="Type of request (analyze, fetch_drug, etc.)")
    endpoint: str = Field(..., description="API endpoint called")
    
    # Drug information
    drug_name: Optional[str] = Field(None, description="Drug being analyzed")
    smiles: Optional[str] = Field(None, description="SMILES string analyzed")
    
    # Performance metrics
    response_time_ms: float = Field(0.0, ge=0, description="Response time in milliseconds")
    status_code: int = Field(200, description="HTTP status code")
    
    # Error tracking
    is_error: bool = Field(False, description="Whether request had error")
    error_message: Optional[str] = Field(None, description="Error message if any")
    
    # Cache tracking
    was_cached: bool = Field(False, description="Whether result was cached")
    cache_hit: bool = Field(False, description="Whether request hit cache")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When request was made")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "req-123456",
                "request_type": "analyze",
                "endpoint": "/api/analyze",
                "drug_name": "Aspirin",
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "response_time_ms": 150.5,
                "status_code": 200,
                "is_error": False,
                "error_message": None,
                "was_cached": False,
                "cache_hit": False,
                "timestamp": "2026-03-21T10:30:45.123456"
            }
        }
    )
    
    class Settings:
        """✅ MongoDB Collection Configuration"""
        name = "api_analytics"
        
        # Indexes for fast queries
        indexes = [
            ("request_id",),           # Fast lookup by request ID
            ("request_type",),         # Filter by request type
            ("endpoint",),             # Filter by endpoint
            ("drug_name",),            # Filter by drug name
            ("timestamp",),            # Time-based queries
            ("is_error",),             # Filter errors
            ("was_cached",),           # Filter cached requests
            [("timestamp", ASCENDING), ("endpoint", ASCENDING)],  # Combined queries
        ]
    
    def __str__(self) -> str:
        return f"APIAnalytics({self.request_type}, {self.endpoint}, {self.response_time_ms}ms)"


# ✅ Analytics Summary Data Model
class AnalyticsSummary(Document):
    """✅ Daily Analytics Summary - MongoDB Document"""
    
    # Date tracking
    date: str = Field(..., description="Date of analytics (YYYY-MM-DD)")
    
    # Request metrics
    total_requests: int = Field(0, ge=0, description="Total API requests")
    total_errors: int = Field(0, ge=0, description="Total failed requests")
    total_cache_hits: int = Field(0, ge=0, description="Total cache hits")
    
    # Performance metrics
    avg_response_time_ms: float = Field(0.0, ge=0, description="Average response time")
    min_response_time_ms: float = Field(0.0, ge=0, description="Minimum response time")
    max_response_time_ms: float = Field(0.0, ge=0, description="Maximum response time")
    
    # Most analyzed
    most_analyzed_drugs: Optional[str] = Field(None, description="Top drugs analyzed (JSON string)")
    
    # Cache metrics
    cache_hit_rate: float = Field(0.0, ge=0, le=100, description="Cache hit rate percentage")
    
    # Endpoint statistics
    endpoint_stats: Optional[str] = Field(None, description="Endpoint usage stats (JSON string)")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When summary was created")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2026-03-21",
                "total_requests": 150,
                "total_errors": 5,
                "total_cache_hits": 45,
                "avg_response_time_ms": 125.5,
                "min_response_time_ms": 50.2,
                "max_response_time_ms": 500.8,
                "most_analyzed_drugs": '{"Aspirin": 25, "Atorvastatin": 20}',
                "cache_hit_rate": 30.0,
                "endpoint_stats": '{"​/api/analyze": 100, "/api/drugs": 50}',
                "timestamp": "2026-03-21T10:30:45.123456"
            }
        }
    )
    
    class Settings:
        """✅ MongoDB Collection Configuration"""
        name = "analytics_summary"
        
        # Indexes for fast queries
        indexes = [
            ("date",),                 # Fast lookup by date
            ("timestamp",),            # Time-based queries
            [("date", ASCENDING)],     # Date sorting
        ]
    
    def __str__(self) -> str:
        return f"AnalyticsSummary({self.date}, {self.total_requests} requests)"


# ✅ Export Response Model
class ExportResponse(Document):
    """✅ Data Export Response Model"""
    
    status: str = Field(..., description="Export status (success/error)")
    format: str = Field(..., description="Export format (json/csv)")
    total_records: int = Field(0, ge=0, description="Total records exported")
    data: Optional[str] = Field(None, description="Exported data")
    filename: Optional[str] = Field(None, description="Generated filename")
    exported_at: datetime = Field(default_factory=datetime.utcnow, description="When data was exported")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "format": "json",
                "total_records": 13,
                "data": '[{"_id": "123", "drug_name": "Aspirin", ...}]',
                "filename": "analyses_20260321_103045.json",
                "exported_at": "2026-03-21T10:30:45.123456"
            }
        }
    )
    
    class Settings:
        """✅ MongoDB Collection Configuration"""
        name = "export_responses"
        
        indexes = [
            ("exported_at",),
            ("format",),
        ]


# ✅ Cache Statistics Model
class CacheStatistics(Document):
    """✅ Cache Performance Statistics"""
    
    cache_enabled: bool = Field(True, description="Is cache enabled?")
    cache_type: str = Field("In-Memory (Zero Installation, Zero Storage!)", description="Type of cache")
    total_cached: int = Field(0, ge=0, description="How many items cached")
    max_size: int = Field(1000, ge=0, description="Cache size limit")
    hit_count: int = Field(0, ge=0, description="Total cache hits")
    miss_count: int = Field(0, ge=0, description="Total cache misses")
    hit_rate: float = Field(0.0, ge=0, le=100, description="Hit rate percentage")
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When stats were recorded")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cache_enabled": True,
                "cache_type": "In-Memory (Zero Installation, Zero Storage!)",
                "total_cached": 5,
                "max_size": 1000,
                "hit_count": 2,
                "miss_count": 1,
                "hit_rate": 66.67,
                "recorded_at": "2026-03-21T10:30:45.123456"
            }
        }
    )
    
    class Settings:
        """✅ MongoDB Collection Configuration"""
        name = "cache_statistics"
        
        indexes = [
            ("recorded_at",),
        ]


# ✅ Performance Metrics Model
class PerformanceMetrics(Document):
    """✅ API Performance Metrics"""
    
    endpoint: str = Field(..., description="API endpoint")
    request_type: str = Field(..., description="Type of request")
    
    # Response time metrics
    avg_response_time_ms: float = Field(0.0, ge=0, description="Average response time")
    min_response_time_ms: float = Field(0.0, ge=0, description="Minimum response time")
    max_response_time_ms: float = Field(0.0, ge=0, description="Maximum response time")
    
    # Request metrics
    total_requests: int = Field(0, ge=0, description="Total requests")
    successful_requests: int = Field(0, ge=0, description="Successful requests")
    failed_requests: int = Field(0, ge=0, description="Failed requests")
    
    # Success rate
    success_rate: float = Field(0.0, ge=0, le=100, description="Success rate percentage")
    
    # Time period
    period_start: datetime = Field(..., description="Period start time")
    period_end: datetime = Field(..., description="Period end time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "endpoint": "/api/analyze",
                "request_type": "analyze",
                "avg_response_time_ms": 145.5,
                "min_response_time_ms": 50.2,
                "max_response_time_ms": 500.8,
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5,
                "success_rate": 95.0,
                "period_start": "2026-03-21T00:00:00Z",
                "period_end": "2026-03-21T23:59:59Z"
            }
        }
    )
    
    class Settings:
        """✅ MongoDB Collection Configuration"""
        name = "performance_metrics"
        
        indexes = [
            ("endpoint",),
            ("request_type",),
            ("period_start",),
            [("endpoint", ASCENDING), ("period_start", ASCENDING)],
        ]
    
    def __str__(self) -> str:
        return f"PerformanceMetrics({self.endpoint}, {self.success_rate}% success)"