"""
Long-term Memory Bank for storing and retrieving contextual information
"""
from typing import Dict, Any, List, Optional
from collections import deque
import structlog
from datetime import datetime

logger = structlog.get_logger()


class MemoryBank:
    """
    Memory Bank for long-term storage of agent interactions and knowledge
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.memories: deque = deque(maxlen=max_size)
        self.index: Dict[str, List[int]] = {}  # keyword -> memory indices
    
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> int:
        """Add a memory to the bank"""
        memory = {
            "id": len(self.memories),
            "content": content,
            "metadata": metadata or {},
            "importance": importance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.memories.append(memory)
        
        # Index by keywords
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            self.index[keyword].append(memory["id"])
        
        logger.debug("Memory added", memory_id=memory["id"], importance=importance)
        return memory["id"]
    
    def retrieve_memories(
        self,
        query: str,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query"""
        query_keywords = self._extract_keywords(query.lower())
        
        # Find memories with matching keywords
        memory_scores: Dict[int, float] = {}
        for keyword in query_keywords:
            if keyword in self.index:
                for memory_id in self.index[keyword]:
                    if memory_id not in memory_scores:
                        memory_scores[memory_id] = 0.0
                    memory_scores[memory_id] += 1.0
        
        # Get memories and sort by score and importance
        results = []
        for memory_id, score in memory_scores.items():
            if memory_id < len(self.memories):
                memory = self.memories[memory_id]
                if memory["importance"] >= min_importance:
                    results.append({
                        **memory,
                        "relevance_score": score
                    })
        
        # Sort by relevance score and importance
        results.sort(key=lambda x: (x["relevance_score"], x["importance"]), reverse=True)
        
        return results[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        # Filter out common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return keywords[:10]  # Limit to top 10 keywords
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent memories"""
        return list(self.memories)[-limit:]
    
    def clear(self):
        """Clear all memories"""
        self.memories.clear()
        self.index.clear()
        logger.info("Memory bank cleared")

