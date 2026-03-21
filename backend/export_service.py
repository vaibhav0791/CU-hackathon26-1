import csv
import json
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ExportService:
    """✅ V-6: Data Export Service"""
    
    @staticmethod
    async def export_to_json(analyses: List[Dict[str, Any]], pretty: bool = True) -> str:
        """Export analyses to JSON format"""
        try:
            if pretty:
                return json.dumps(analyses, indent=2, default=str)
            else:
                return json.dumps(analyses, default=str)
        except Exception as e:
            logger.error(f"JSON export error: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    async def export_to_csv(analyses: List[Dict[str, Any]]) -> str:
        """Export analyses to CSV format"""
        try:
            if not analyses:
                return "No data to export"
            
            # Get all unique keys
            all_keys = set()
            for analysis in analyses:
                all_keys.update(analysis.keys())
            
            fieldnames = sorted(list(all_keys))
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for analysis in analyses:
                # Convert None to empty string
                row = {k: analysis.get(k, '') for k in fieldnames}
                writer.writerow(row)
            
            return output.getvalue()
        except Exception as e:
            logger.error(f"CSV export error: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    async def filter_analyses(
        analyses: List[Dict[str, Any]],
        drug_name: Optional[str] = None,
        bcs_class: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_solubility: Optional[float] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter analyses based on criteria"""
        filtered = analyses.copy()
        
        # Filter by drug name
        if drug_name:
            filtered = [a for a in filtered if drug_name.lower() in a.get('drug_name', '').lower()]
        
        # Filter by BCS class
        if bcs_class:
            filtered = [a for a in filtered if a.get('bcs_class') == bcs_class]
        
        # Filter by minimum confidence
        if min_confidence is not None:
            filtered = [a for a in filtered if a.get('confidence_score', 0) >= min_confidence]
        
        # Filter by maximum solubility
        if max_solubility is not None:
            filtered = [a for a in filtered if a.get('solubility_score', 0) <= max_solubility]
        
        # Filter by date range
        if date_from or date_to:
            filtered_by_date = []
            for analysis in filtered:
                timestamp = analysis.get('created_at', '')
                if date_from and timestamp < date_from:
                    continue
                if date_to and timestamp > date_to:
                    continue
                filtered_by_date.append(analysis)
            filtered = filtered_by_date
        
        logger.info(f"Filtered analyses: {len(filtered)} records from {len(analyses)} total")
        return filtered
    
    @staticmethod
    async def export_analytics_json(
        analytics: List[Dict[str, Any]],
        pretty: bool = True
    ) -> str:
        """Export analytics to JSON format"""
        try:
            if pretty:
                return json.dumps(analytics, indent=2, default=str)
            else:
                return json.dumps(analytics, default=str)
        except Exception as e:
            logger.error(f"Analytics JSON export error: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    async def export_analytics_csv(analytics: List[Dict[str, Any]]) -> str:
        """Export analytics to CSV format"""
        try:
            if not analytics:
                return "No analytics data to export"
            
            # Get all unique keys
            all_keys = set()
            for record in analytics:
                all_keys.update(record.keys())
            
            fieldnames = sorted(list(all_keys))
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for record in analytics:
                row = {k: record.get(k, '') for k in fieldnames}
                writer.writerow(row)
            
            return output.getvalue()
        except Exception as e:
            logger.error(f"Analytics CSV export error: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def get_export_filename(export_type: str, data_type: str = "analyses") -> str:
        """Generate filename for export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{data_type}_{timestamp}.{export_type}"