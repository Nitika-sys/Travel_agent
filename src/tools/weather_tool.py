"""
Weather Tool - LangChain Custom Tool
=====================================
This tool fetches real-time weather data from Open-Meteo API (free, no API key required).
"""

from typing import Optional, Dict, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import requests
from datetime import datetime, timedelta


class WeatherInput(BaseModel):
    """Input schema for weather tool."""
    city: str = Field(description="City name (e.g., Goa, Bangalore, Delhi)")
    days: Optional[int] = Field(
        default=7,
        description="Number of days for forecast (1-7)"
    )


class WeatherTool(BaseTool):
    """
    LangChain tool for fetching weather data from Open-Meteo API.
    
    Capabilities:
    - Fetches real-time weather forecast
    - No API key required
    - Provides temperature, conditions, precipitation
    - Up to 7-day forecast
    """
    
    name: str = "weather_lookup"
    description: str = """
    Fetches weather forecast for a city.
    Input should be city name and number of forecast days (1-7).
    Returns temperature, weather conditions, and precipitation info.
    Use this when user asks about weather or climate for their trip.
    """
    args_schema: type[BaseModel] = WeatherInput
    
    # City coordinates mapping (major Indian cities)
    CITY_COORDINATES = {
        "goa": {"lat": 15.2993, "lon": 74.1240, "name": "Goa"},
        "bangalore": {"lat": 12.9716, "lon": 77.5946, "name": "Bangalore"},
        "bengaluru": {"lat": 12.9716, "lon": 77.5946, "name": "Bangalore"},
        "delhi": {"lat": 28.7041, "lon": 77.1025, "name": "Delhi"},
        "mumbai": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
        "chennai": {"lat": 13.0827, "lon": 80.2707, "name": "Chennai"},
        "kolkata": {"lat": 22.5726, "lon": 88.3639, "name": "Kolkata"},
        "hyderabad": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad"},
        "pune": {"lat": 18.5204, "lon": 73.8567, "name": "Pune"},
        "jaipur": {"lat": 26.9124, "lon": 75.7873, "name": "Jaipur"},
        "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "name": "Ahmedabad"},
        "lucknow": {"lat": 26.8467, "lon": 80.9462, "name": "Lucknow"},
        "udaipur": {"lat": 24.5854, "lon": 73.7125, "name": "Udaipur"},
        "agra": {"lat": 27.1767, "lon": 78.0081, "name": "Agra"},
        "varanasi": {"lat": 25.3176, "lon": 82.9739, "name": "Varanasi"}
    }
    
    def __init__(self):
        """Initialize weather tool."""
        super().__init__()
        self.api_base_url = "https://api.open-meteo.com/v1/forecast"
    
    def _get_coordinates(self, city: str) -> Optional[Dict]:
        """
        Get latitude and longitude for a city.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with lat, lon, name or None
        """
        city_key = city.lower().strip()
        return self.CITY_COORDINATES.get(city_key)
    
    def _interpret_weather_code(self, code: int) -> str:
        """
        Interpret WMO weather code.
        
        Args:
            code: WMO weather code
            
        Returns:
            Human-readable weather description
        """
        weather_codes = {
            0: "Clear Sky ☀️",
            1: "Mainly Clear 🌤️",
            2: "Partly Cloudy ⛅",
            3: "Overcast ☁️",
            45: "Foggy 🌫️",
            48: "Foggy 🌫️",
            51: "Light Drizzle 🌦️",
            53: "Moderate Drizzle 🌦️",
            55: "Dense Drizzle 🌧️",
            61: "Slight Rain 🌧️",
            63: "Moderate Rain 🌧️",
            65: "Heavy Rain ⛈️",
            71: "Slight Snow ❄️",
            73: "Moderate Snow ❄️",
            75: "Heavy Snow ❄️",
            80: "Rain Showers 🌦️",
            81: "Rain Showers 🌧️",
            82: "Heavy Showers ⛈️",
            95: "Thunderstorm ⛈️",
            96: "Thunderstorm with Hail ⛈️",
            99: "Heavy Thunderstorm ⛈️"
        }
        return weather_codes.get(code, "Unknown")
    
    def _fetch_weather_data(
        self,
        latitude: float,
        longitude: float,
        days: int
    ) -> Optional[Dict]:
        """
        Fetch weather data from Open-Meteo API.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of forecast days
            
        Returns:
            Weather data dictionary or None
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "weathercode",
                    "precipitation_sum",
                    "precipitation_probability_max"
                ],
                "timezone": "auto",
                "forecast_days": min(days, 7)
            }
            
            response = requests.get(self.api_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def _format_weather_output(
        self,
        city_name: str,
        weather_data: Dict,
        days: int
    ) -> str:
        """
        Format weather data for agent consumption.
        
        Args:
            city_name: Name of the city
            weather_data: Raw weather data from API
            days: Number of days
            
        Returns:
            Formatted weather forecast string
        """
        try:
            daily = weather_data.get("daily", {})
            dates = daily.get("time", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            weather_codes = daily.get("weathercode", [])
            precipitation = daily.get("precipitation_sum", [])
            precip_prob = daily.get("precipitation_probability_max", [])
            
            output = f"🌤️ Weather Forecast for {city_name}:\n\n"
            
            for i in range(min(days, len(dates))):
                date_obj = datetime.fromisoformat(dates[i])
                day_name = date_obj.strftime("%A, %b %d")
                
                condition = self._interpret_weather_code(weather_codes[i])
                temp_high = temp_max[i]
                temp_low = temp_min[i]
                rain = precipitation[i] if i < len(precipitation) else 0
                rain_prob = precip_prob[i] if i < len(precip_prob) else 0
                
                output += f"Day {i+1} ({day_name}):\n"
                output += f"  Condition: {condition}\n"
                output += f"  Temperature: {temp_high}°C (High) / {temp_low}°C (Low)\n"
                
                if rain > 0 or rain_prob > 20:
                    output += f"  Precipitation: {rain}mm ({rain_prob}% chance)\n"
                
                output += "\n"
            
            # Add travel recommendation
            avg_temp = sum(temp_max[:days]) / days
            has_rain = any(p > 5 for p in precipitation[:days])
            
            output += "💡 Travel Tips:\n"
            if avg_temp > 30:
                output += "  • Pack light, breathable clothing and sunscreen\n"
            elif avg_temp < 20:
                output += "  • Bring warm layers and a jacket\n"
            else:
                output += "  • Pleasant weather, comfortable clothing recommended\n"
            
            if has_rain:
                output += "  • Carry an umbrella or raincoat\n"
            else:
                output += "  • No rain expected, perfect for outdoor activities\n"
            
            return output
            
        except Exception as e:
            return f"Error formatting weather data: {str(e)}"
    
    def _run(self, city: str, days: int = 7) -> str:
        """
        Execute weather lookup.
        
        Args:
            city: City name
            days: Number of forecast days
            
        Returns:
            Formatted weather forecast
        """
        try:
            # Get coordinates
            coords = self._get_coordinates(city)
            
            if not coords:
                available = ", ".join(sorted(set(c["name"] for c in self.CITY_COORDINATES.values())))
                return (f"City '{city}' not found in database. "
                       f"Available cities: {available}")
            
            # Fetch weather data
            weather_data = self._fetch_weather_data(
                coords["lat"],
                coords["lon"],
                days
            )
            
            if not weather_data:
                return f"Failed to fetch weather data for {coords['name']}. Please try again."
            
            # Format and return
            return self._format_weather_output(coords["name"], weather_data, days)
            
        except Exception as e:
            return f"Error in weather lookup: {str(e)}"


