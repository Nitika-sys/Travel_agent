"""
Data Loader Utility
===================
Handles loading and caching of JSON data files.
"""

import json
import os
from typing import Dict, List, Optional
from functools import lru_cache


class DataLoader:
    """
    Efficient data loader with caching for JSON files.
    """
    
    def __init__(self, data_path: str = "data/"):
        """
        Initialize data loader.
        
        Args:
            data_path: Base path for data files
        """
        self.data_path = data_path
    
    @lru_cache(maxsize=10)
    def load_json(self, filename: str) -> List[Dict]:
        """
        Load JSON file with caching.
        
        Args:
            filename: Name of JSON file
            
        Returns:
            List of dictionaries from JSON
            
        Raises:
            FileNotFoundError: If file doesn't exist
            JSONDecodeError: If JSON is malformed
        """
        filepath = os.path.join(self.data_path, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both list and dict with data key
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common keys
                for key in ['flights', 'hotels', 'places', 'data']:
                    if key in data:
                        return data[key]
                return [data]  # Wrap single dict in list
            else:
                return []
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
    
    def load_flights(self) -> List[Dict]:
        """Load flights data."""
        return self.load_json("flights.json")
    
    def load_hotels(self) -> List[Dict]:
        """Load hotels data."""
        return self.load_json("hotels.json")
    
    def load_places(self) -> List[Dict]:
        """Load places data."""
        return self.load_json("places.json")
    
    def clear_cache(self):
        """Clear the cache."""
        self.load_json.cache_clear()

