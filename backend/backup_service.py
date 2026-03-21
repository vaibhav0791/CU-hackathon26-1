import sqlite3
import shutil
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import gzip
from bson import ObjectId

logger = logging.getLogger(__name__)

class BackupService:
    """✅ V-8: Database Backup & Recovery Service"""
    
    def __init__(self, db_path: str = "pharma.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        logger.info(f"Backup service initialized. Backup directory: {self.backup_dir}")
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    async def create_full_backup(self, compress: bool = True) -> Dict[str, Any]:
        """
        ✅ V-8: Create full database backup
        
        Returns:
            Dict with backup info (path, size, timestamp, etc.)
        """
        try:
            timestamp = self._get_timestamp()
            backup_filename = f"pharma_full_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ Full backup created: {backup_path}")
            
            # Get backup size
            backup_size = backup_path.stat().st_size
            
            # Compress if requested
            compressed_path = None
            compressed_size = None
            if compress:
                compressed_filename = f"{backup_filename}.gz"
                compressed_path = self.backup_dir / compressed_filename
                
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                compressed_size = compressed_path.stat().st_size
                logger.info(f"✅ Backup compressed: {compressed_path}")
                
                # Remove uncompressed backup
                backup_path.unlink()
                backup_path = compressed_path
            
            backup_info = {
                "_id": str(ObjectId()),
                "backup_type": "full",
                "filename": backup_path.name,
                "path": str(backup_path),
                "size_bytes": compressed_size if compress else backup_size,
                "compressed": compress,
                "original_size_bytes": backup_size,
                "compression_ratio": round(compressed_size / backup_size * 100, 2) if compress else 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success"
            }
            
            return backup_info
        
        except Exception as e:
            logger.error(f"❌ Full backup failed: {type(e).__name__}: {e}")
            return {
                "backup_type": "full",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def create_incremental_backup(self) -> Dict[str, Any]:
        """
        ✅ V-8: Create incremental backup (recent changes only)
        """
        try:
            timestamp = self._get_timestamp()
            
            # Get list of recent analysis records
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get records from last backup
            one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            cursor.execute(
                "SELECT * FROM analysis_blueprint WHERE updated_at > ?",
                (one_day_ago,)
            )
            recent_analyses = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute(
                "SELECT * FROM api_analytics WHERE timestamp > ?",
                (one_day_ago,)
            )
            recent_analytics = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            # Create incremental backup file
            backup_filename = f"pharma_incremental_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            incremental_data = {
                "backup_type": "incremental",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "period": f"Last 24 hours from {one_day_ago}",
                "analyses": recent_analyses,
                "analytics": recent_analytics,
                "total_records": len(recent_analyses) + len(recent_analytics)
            }
            
            with open(backup_path, 'w') as f:
                json.dump(incremental_data, f, indent=2, default=str)
            
            backup_size = backup_path.stat().st_size
            logger.info(f"✅ Incremental backup created: {backup_path}")
            
            backup_info = {
                "_id": str(ObjectId()),
                "backup_type": "incremental",
                "filename": backup_filename,
                "path": str(backup_path),
                "size_bytes": backup_size,
                "records_backed_up": incremental_data["total_records"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success"
            }
            
            return backup_info
        
        except Exception as e:
            logger.error(f"❌ Incremental backup failed: {type(e).__name__}: {e}")
            return {
                "backup_type": "incremental",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        ✅ V-8: List all available backups
        """
        try:
            backups = []
            
            for backup_file in sorted(self.backup_dir.iterdir(), reverse=True):
                if backup_file.is_file():
                    size = backup_file.stat().st_size
                    
                    # Determine backup type
                    if "full" in backup_file.name:
                        b_type = "full"
                    elif "incremental" in backup_file.name:
                        b_type = "incremental"
                    else:
                        b_type = "unknown"
                    
                    if backup_type and b_type != backup_type:
                        continue
                    
                    # Extract timestamp from filename
                    parts = backup_file.name.split("_")
                    timestamp_str = "_".join(parts[-2:]).replace(".db", "").replace(".gz", "").replace(".json", "")
                    
                    backup_info = {
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size_bytes": size,
                        "backup_type": b_type,
                        "created_at": backup_file.stat().st_ctime,
                        "timestamp": timestamp_str
                    }
                    
                    backups.append(backup_info)
            
            logger.info(f"Found {len(backups)} backups")
            return backups
        
        except Exception as e:
            logger.error(f"❌ List backups failed: {type(e).__name__}: {e}")
            return []
    
    async def restore_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        ✅ V-8: Restore database from backup
        
        WARNING: This will overwrite the current database!
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                return {
                    "status": "error",
                    "error": f"Backup file not found: {backup_filename}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Create safety backup of current database
            safety_backup = self.db_path.replace(".db", f"_safety_backup_{self._get_timestamp()}.db")
            shutil.copy2(self.db_path, safety_backup)
            logger.info(f"✅ Safety backup created: {safety_backup}")
            
            # Handle compressed backup
            if backup_filename.endswith(".gz"):
                temp_db = self.db_path.replace(".db", "_temp.db")
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                shutil.move(temp_db, self.db_path)
                logger.info(f"✅ Decompressed and restored from: {backup_filename}")
            else:
                # Handle JSON incremental backup
                if backup_filename.endswith(".json"):
                    with open(backup_path, 'r') as f:
                        incremental_data = json.load(f)
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Insert analyses
                    for analysis in incremental_data.get("analyses", []):
                        cursor.execute('''
                            INSERT OR REPLACE INTO analysis_blueprint 
                            (_id, drug_name, smiles, bcs_class, solubility_score, 
                             confidence_score, molecular_weight, timestamp, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            analysis.get('_id'),
                            analysis.get('drug_name'),
                            analysis.get('smiles'),
                            analysis.get('bcs_class'),
                            analysis.get('solubility_score'),
                            analysis.get('confidence_score'),
                            analysis.get('molecular_weight'),
                            analysis.get('timestamp'),
                            analysis.get('created_at'),
                            analysis.get('updated_at')
                        ))
                    
                    conn.commit()
                    conn.close()
                    logger.info(f"✅ Restored {len(incremental_data.get('analyses', []))} analyses from incremental backup")
                
                else:
                    # Direct database copy
                    shutil.copy2(backup_path, self.db_path)
                    logger.info(f"✅ Restored from: {backup_filename}")
            
            restore_info = {
                "status": "success",
                "backup_file": backup_filename,
                "restored_at": datetime.now(timezone.utc).isoformat(),
                "safety_backup": safety_backup,
                "message": "Database successfully restored. Previous database backed up to safety_backup."
            }
            
            return restore_info
        
        except Exception as e:
            logger.error(f"❌ Restore failed: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def delete_old_backups(self, days: int = 30) -> Dict[str, Any]:
        """
        ✅ V-8: Delete backups older than specified days
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            deleted_count = 0
            freed_space = 0
            
            for backup_file in self.backup_dir.iterdir():
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime, tz=timezone.utc)
                    
                    if file_time < cutoff_time:
                        freed_space += backup_file.stat().st_size
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted old backup: {backup_file.name}")
            
            return {
                "status": "success",
                "deleted_backups": deleted_count,
                "freed_space_bytes": freed_space,
                "freed_space_mb": round(freed_space / (1024 * 1024), 2),
                "cutoff_date": cutoff_time.isoformat(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Delete old backups failed: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def validate_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        ✅ V-8: Validate backup integrity
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                return {
                    "status": "error",
                    "valid": False,
                    "error": f"Backup file not found: {backup_filename}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Check file size
            file_size = backup_path.stat().st_size
            if file_size == 0:
                return {
                    "status": "error",
                    "valid": False,
                    "error": "Backup file is empty",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Try to open and verify
            try:
                if backup_filename.endswith(".gz"):
                    with gzip.open(backup_path, 'rb') as f:
                        f.read(1024)  # Read first 1KB to verify integrity
                    logger.info(f"✅ Backup verified: {backup_filename}")
                
                elif backup_filename.endswith(".json"):
                    with open(backup_path, 'r') as f:
                        json.load(f)  # Verify JSON is valid
                    logger.info(f"✅ Backup verified: {backup_filename}")
                
                else:
                    # Verify SQLite database
                    conn = sqlite3.connect(backup_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM analysis_blueprint")
                    count = cursor.fetchone()[0]
                    conn.close()
                    logger.info(f"✅ Backup verified: {backup_filename} ({count} records)")
                
                return {
                    "status": "success",
                    "valid": True,
                    "backup_file": backup_filename,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            except Exception as verify_error:
                return {
                    "status": "error",
                    "valid": False,
                    "error": f"Backup integrity check failed: {str(verify_error)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except Exception as e:
            logger.error(f"❌ Validate backup failed: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "valid": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_backup_stats(self) -> Dict[str, Any]:
        """
        ✅ V-8: Get backup statistics
        """
        try:
            backups = await self.list_backups()
            
            total_size = sum([b.get("size_bytes", 0) for b in backups])
            full_backups = [b for b in backups if b.get("backup_type") == "full"]
            incremental_backups = [b for b in backups if b.get("backup_type") == "incremental"]
            
            return {
                "total_backups": len(backups),
                "full_backups": len(full_backups),
                "incremental_backups": len(incremental_backups),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_backup": backups[-1].get("filename") if backups else None,
                "latest_backup": backups[0].get("filename") if backups else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Get backup stats failed: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }