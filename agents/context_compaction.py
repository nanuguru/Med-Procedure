"""
Context Compaction - Reduces context size while preserving important information
"""
from typing import Dict, Any, Optional
import structlog
from config import settings

logger = structlog.get_logger()


class ContextCompactor:
    """Compacts context to reduce size while maintaining important information"""
    
    def __init__(self):
        self.compaction_threshold = settings.context_compaction_threshold
    
    async def compact(
        self,
        data: Dict[str, Any],
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Compact context data
        
        Args:
            data: Data to compact
            threshold: Compaction threshold (0.0 to 1.0)
        """
        if threshold is None:
            threshold = self.compaction_threshold
        
        # Calculate data size (simplified)
        data_size = self._estimate_size(data)
        
        # If size is acceptable, return as is
        if data_size < threshold * 1000:  # Simplified threshold
            return data
        
        # Compact the data
        compacted = {}
        
        # Preserve essential fields
        essential_fields = [
            "service_name", "setting", "procedure_details",
            "validation", "equipment", "context"
        ]
        
        for field in essential_fields:
            if field in data:
                compacted[field] = data[field]
        
        # Compact procedure_details if it's a string
        if "procedure_details" in compacted:
            if isinstance(compacted["procedure_details"], str):
                # Truncate if too long
                max_length = 2000
                if len(compacted["procedure_details"]) > max_length:
                    compacted["procedure_details"] = (
                        compacted["procedure_details"][:max_length] + "..."
                    )
        
        # Compact references
        if "references" in data:
            # Keep only top 5 references
            compacted["references"] = data["references"][:5]
        
        logger.debug(
            "Context compacted",
            original_size=data_size,
            compacted_size=self._estimate_size(compacted)
        )
        
        return compacted
    
    def _estimate_size(self, data: Dict[str, Any]) -> int:
        """Estimate size of data structure"""
        import json
        try:
            return len(json.dumps(data))
        except:
            return len(str(data))

