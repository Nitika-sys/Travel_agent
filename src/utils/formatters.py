"""
Output Formatters
=================
Utility functions for formatting outputs.
"""

from typing import Dict, List
from datetime import datetime


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Numeric amount
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_date_range(start_date: str, end_date: str) -> str:
    """
    Format date range in readable format.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Formatted date range string
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"


def format_itinerary_text(itinerary: Dict) -> str:
    """
    Format itinerary as plain text.
    
    Args:
        itinerary: Itinerary dictionary
        
    Returns:
        Formatted text itinerary
    """
    output = []
    output.append("=" * 70)
    output.append(f"YOUR {itinerary['num_days']}-DAY TRIP TO {itinerary['destination'].upper()}")
    output.append(f"{itinerary['start_date']} to {itinerary['end_date']}")
    output.append("=" * 70)
    output.append("")
    
    # Flight
    flight = itinerary['flight']
    output.append("✈️  FLIGHT SELECTED")
    output.append("-" * 70)
    output.append(f"Airline: {flight['airline']} ({flight['flight_id']})")
    output.append(f"Price: {format_currency(flight['price'])}")
    output.append(f"Departure: {flight['departure']} | Arrival: {flight['arrival']}")
    output.append(f"Duration: {flight['duration']}")
    output.append("")
    
    # Hotel
    hotel = itinerary['hotel']
    output.append("🏨 HOTEL BOOKED")
    output.append("-" * 70)
    output.append(f"Hotel: {hotel['name']}")
    output.append(f"Rating: ⭐ {hotel['rating']}/5")
    output.append(f"Price: {format_currency(hotel['price_per_night'])}/night")
    output.append(f"Amenities: {', '.join(hotel['amenities'])}")
    output.append("")
    
    # Weather
    output.append("🌤️  WEATHER FORECAST")
    output.append("-" * 70)
    for w in itinerary['weather']:
        output.append(f"Day {w['day']} ({w['date']}): {w['condition']} - {w['temp_high']}°C")
    output.append("")
    
    # Itinerary
    output.append("📅 DAY-WISE ITINERARY")
    output.append("-" * 70)
    for day in itinerary['daily_itinerary']:
        output.append(f"\nDay {day['day']}: {day['title']}")
        for activity in day['activities']:
            output.append(f"  📍 {activity['name']} ({activity['type']}, ⭐ {activity['rating']})")
            output.append(f"     {activity['description']}")
    output.append("")
    
    # Budget
    budget = itinerary['budget']
    output.append("💰 BUDGET BREAKDOWN")
    output.append("-" * 70)
    output.append(f"Flight:              {format_currency(budget['flight'])}")
    output.append(f"Hotel:               {format_currency(budget['hotel'])}")
    output.append(f"Food & Travel:       {format_currency(budget['food_and_travel'])}")
    output.append(f"Activities:          {format_currency(budget['activities'])}")
    output.append("-" * 70)
    output.append(f"TOTAL COST:          {format_currency(budget['total'])}")
    output.append("=" * 70)
    
    return "\n".join(output)

