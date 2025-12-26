"""
Configuration Module
====================
Centralized configuration for the application.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Agent Settings
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
    
    # Data Paths
    DATA_PATH: str = os.getenv("DATA_PATH", "./data/")
    FLIGHTS_FILE: str = os.getenv("FLIGHTS_FILE", "flights.json")
    HOTELS_FILE: str = os.getenv("HOTELS_FILE", "hotels.json")
    PLACES_FILE: str = os.getenv("PLACES_FILE", "places.json")
    
    # Weather API
    WEATHER_API_URL: str = os.getenv(
        "WEATHER_API_URL",
        "https://api.open-meteo.com/v1/forecast"
    )
    
    # Application Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configurations are set.
        
        Returns:
            True if valid, False otherwise
        """
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            print("Warning: No API keys configured!")
            return False
        return True
    
    @classmethod
    def get_data_file_path(cls, filename: str) -> str:
        """
        Get full path for a data file.
        
        Args:
            filename: Name of the data file
            
        Returns:
            Full path to the file
        """
        return os.path.join(cls.DATA_PATH, filename)


# Validate configuration on import
Config.validate()

