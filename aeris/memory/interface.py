from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict

class MemoryInterface(ABC):
    """
    Foundation for Aeris Memory.
    Part 1 focuses on the abstraction. Later parts will implement vector DBs 
    or SQLite-backed long-term memory.
    """

    @abstractmethod
    def add(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Add an item to memory."""
        pass

    @abstractmethod
    def retrieve(self, query: str) -> List[Any]:
        """Retrieve items from memory based on a query."""
        pass

    @abstractmethod
    def update(self, key: str, value: Any):
        """Update an existing memory item."""
        pass

    @abstractmethod
    def delete(self, key: str):
        """Delete an item from memory."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all memory (or session memory)."""
        pass

class SessionMemory(MemoryInterface):
    """A simple in-memory implementation for Part 1."""
    
    def __init__(self):
        self._store = {}
        
    def add(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        self._store[key] = {"value": value, "metadata": metadata or {}}
        
    def retrieve(self, query: str) -> List[Any]:
        # Simple exact key match or substring match in key
        results = []
        for k, v in self._store.items():
            if query in k or (isinstance(v["value"], str) and query in v["value"]):
                results.append(v)
        return results

    def update(self, key: str, value: Any):
        if key in self._store:
            self._store[key]["value"] = value
            
    def delete(self, key: str):
        if key in self._store:
            del self._store[key]
            
    def clear(self):
        self._store.clear()
