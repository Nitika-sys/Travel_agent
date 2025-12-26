from typing import Optional, Dict, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime


class FlightSearchInput(BaseModel):
    """Input schema for flight search tool."""
    source: str = Field(description="Source city (e.g., Delhi, Mumbai)")
    destination: str = Field(description="Destination city (e.g., Goa, Bangalore)")
    sort_by: Optional[str] = Field(
        default="price",
        description="Sort criteria: 'price' for cheapest, 'duration' for fastest"
    )


class FlightSearchTool(BaseTool):
    """
    LangChain tool for searching flights from JSON dataset.
    
    Capabilities:
    - Filters flights by source and destination
    - Sorts by price or duration
    - Returns top 3 flight options
    - Provides detailed flight information
    """
    
    name: str = "flight_search"
    description: str = """
    Searches for flights between two cities. 
    Input should be source city, destination city, and optional sort preference.
    Returns the best flight options with prices, timings, and airlines.
    Use this when user asks about flights or travel between cities.
    """
    args_schema: type[BaseModel] = FlightSearchInput
    
    def __init__(self, data_path: str = "data/flights.json"):
        """
        Initialize flight search tool.
        
        Args:
            data_path: Path to flights JSON file
        """
        super().__init__()
        self.data_path = data_path
        self.flights_data = self._load_flights()
    
    def _load_flights(self) -> List[Dict]:
        """
        Load flights data from JSON file.
        
        Returns:
            List of flight dictionaries
            
        Raises:
            FileNotFoundError: If flights.json doesn't exist
            JSONDecodeError: If JSON is malformed
        """
        try:
            if not os.path.exists(self.data_path):
                # Return sample data for demonstration
                return self._get_sample_flights()
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get('flights', [])
        except Exception as e:
            print(f"Warning: Could not load flights data: {e}")
            return self._get_sample_flights()
    
    def _get_sample_flights(self) -> List[Dict]:
        """Return sample flight data for demonstration."""
        return [
            {
                "flight_id": "6E-123",
                "airline": "IndiGo",
                "source": "Delhi",
                "destination": "Goa",
                "departure_time": "14:00",
                "arrival_time": "16:30",
                "duration_minutes": 150,
                "price": 4800,
                "available_seats": 45
            },
            {
                "flight_id": "SG-456",
                "airline": "SpiceJet",
                "source": "Delhi",
                "destination": "Goa",
                "departure_time": "09:00",
                "arrival_time": "11:45",
                "duration_minutes": 165,
                "price": 5200,
                "available_seats": 30
            },
            {
                "flight_id": "AI-789",
                "airline": "Air India",
                "source": "Mumbai",
                "destination": "Bangalore",
                "departure_time": "10:30",
                "arrival_time": "12:00",
                "duration_minutes": 90,
                "price": 3500,
                "available_seats": 60
            },
            {
                "flight_id": "UK-321",
                "airline": "Vistara",
                "source": "Bangalore",
                "destination": "Delhi",
                "departure_time": "18:00",
                "arrival_time": "21:00",
                "duration_minutes": 180,
                "price": 6500,
                "available_seats": 25
            },
            {
                "flight_id": "6E-234",
                "airline": "IndiGo",
                "source": "Delhi",
                "destination": "Mumbai",
                "departure_time": "06:00",
                "arrival_time": "08:15",
                "duration_minutes": 135,
                "price": 4200,
                "available_seats": 50
            }
        ]
    
    def _filter_flights(self, source: str, destination: str) -> List[Dict]:
        """
        Filter flights by source and destination.
        
        Args:
            source: Source city name
            destination: Destination city name
            
        Returns:
            List of matching flights
        """
        source_lower = source.lower().strip()
        dest_lower = destination.lower().strip()
        
        filtered = [
            flight for flight in self.flights_data
            if (flight.get('source', '').lower() == source_lower and
                flight.get('destination', '').lower() == dest_lower)
        ]
        
        return filtered
    
    def _format_duration(self, minutes: int) -> str:
        """
        Format duration from minutes to human-readable format.
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            Formatted string (e.g., "2h 30m")
        """
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    
    def _sort_flights(self, flights: List[Dict], sort_by: str) -> List[Dict]:
        """
        Sort flights by specified criteria.
        
        Args:
            flights: List of flight dictionaries
            sort_by: Sort criteria ('price' or 'duration')
            
        Returns:
            Sorted list of flights
        """
        if sort_by == "duration":
            return sorted(flights, key=lambda x: x.get('duration_minutes', 999))
        else:  # Default to price
            return sorted(flights, key=lambda x: x.get('price', 999999))
    
    def _format_flight_output(self, flights: List[Dict]) -> str:
        """
        Format flight results for agent consumption.
        
        Args:
            flights: List of flight dictionaries
            
        Returns:
            Formatted string with flight details
        """
        if not flights:
            return "No flights found for this route."
        
        output = f"Found {len(flights)} flight(s):\n\n"
        
        for i, flight in enumerate(flights[:3], 1):  # Top 3 flights
            duration = self._format_duration(flight.get('duration_minutes', 0))
            output += f"{i}. {flight.get('airline')} ({flight.get('flight_id')})\n"
            output += f"   Route: {flight.get('source')} → {flight.get('destination')}\n"
            output += f"   Price: ₹{flight.get('price'):,}\n"
            output += f"   Departure: {flight.get('departure_time')} | Arrival: {flight.get('arrival_time')}\n"
            output += f"   Duration: {duration}\n"
            output += f"   Available Seats: {flight.get('available_seats')}\n\n"
        
        # Add recommendation
        best = flights[0]
        output += f"💡 Recommendation: {best.get('airline')} offers the best "
        output += "price" if len(flights) > 1 and best.get('price') <= flights[1].get('price', 999999) else "duration"
        output += " for this route.\n"
        
        return output
    
    def _run(self, source: str, destination: str, sort_by: str = "price") -> str:
        """
        Execute flight search.
        
        Args:
            source: Source city
            destination: Destination city
            sort_by: Sorting preference
            
        Returns:
            Formatted flight search results
        """
        try:
            # Filter flights
            matching_flights = self._filter_flights(source, destination)
            
            if not matching_flights:
                return (f"No direct flights found from {source} to {destination}. "
                       f"Please try different cities or check spelling.")
            
            # Sort flights
            sorted_flights = self._sort_flights(matching_flights, sort_by)
            
            # Format output
            return self._format_flight_output(sorted_flights)
            
        except Exception as e:
            return f"Error searching flights: {str(e)}"


