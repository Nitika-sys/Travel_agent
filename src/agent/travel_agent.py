"""
HYBRID TRAVEL AGENT - Works Everywhere! 🌍
============================================
Automatically uses:
- Ollama (when running locally) 
- Gemini (when deployed on Streamlit Cloud)

Just deploy and it works! No configuration needed.
"""

import os
import sys
from typing import Dict, List, Optional
try:
    from langchain.agents import AgentExecutor
except ImportError:
    try:
        from langchain_core.agents import AgentExecutor
    except ImportError:
        from langchain_classic.agents import AgentExecutor
try:
    from langchain.prompts import PromptTemplate
except ImportError:
    from langchain_core.prompts import PromptTemplate
try:
    from langchain.tools import Tool
except ImportError:
    from langchain_core.tools import Tool
import json
from datetime import datetime


class HybridTravelAgent:
    """
    Smart Travel Agent that automatically chooses the best LLM:
    - Local development: Uses Ollama (free, fast, private)
    - Streamlit Cloud: Uses Gemini (free API, easy deploy)
    - Auto-detection: No manual configuration needed!
    """
    
    def __init__(self, temperature: float = 0.7, verbose: bool = True):
        """
        Initialize with automatic LLM detection.
        
        Args:
            temperature: Creativity (0-1)
            verbose: Show reasoning steps
        """
        self.verbose = verbose
        self.temperature = temperature
        
        # Automatically detect and initialize best available LLM
        self.llm, self.provider = self._auto_initialize_llm()
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _auto_initialize_llm(self):
        """
        Automatically detect and initialize the best available LLM.
        Priority: Ollama (local) > Gemini (API) > Demo mode
        
        Returns:
            (llm_instance, provider_name)
        """
        print("🔍 Auto-detecting available LLM...")
        
        # Try Ollama first (best for local development)
        llm, provider = self._try_ollama()
        if llm:
            return llm, provider
        
        # Try Gemini (best for cloud deployment)
        llm, provider = self._try_gemini()
        if llm:
            return llm, provider
        
        # Fallback to demo mode
        print("⚠️  No LLM available, using demo mode")
        print("💡 For AI features: Install Ollama OR get Gemini API key")
        return None, "demo"
    
    def _try_ollama(self):
        """Try to initialize Ollama."""
        try:
            # Check if Ollama is running
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            
            if response.status_code == 200:
                from langchain_community.llms import Ollama
                
                # Check available models
                models = response.json().get('models', [])
                if not models:
                    print("⚠️  Ollama running but no models found")
                    print("💡 Run: ollama pull llama3.2")
                    return None, None
                
                # Use first available model
                model_name = models[0]['name']
                
                llm = Ollama(
                    model=model_name,
                    temperature=self.temperature
                )
                
                print(f"✅ Using Ollama with {model_name} (Local AI)")
                print("🔒 Privacy mode: All data stays on your computer")
                return llm, "ollama"
                
        except ImportError:
            print("📦 langchain-community not installed (needed for Ollama)")
        except Exception as e:
            if self.verbose:
                print(f"ℹ️  Ollama not available: {str(e)[:50]}")
        
        return None, None
    
    def _try_gemini(self):
        """Try to initialize Google Gemini."""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                print("ℹ️  GOOGLE_API_KEY not found")
                return None, None
            
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=self.temperature,
                convert_system_message_to_human=True
            )
            
            print("✅ Using Google Gemini (Cloud AI)")
            print("☁️  Cloud mode: Perfect for Streamlit deployment")
            return llm, "gemini"
            
        except ImportError:
            print("📦 langchain-google-genai not installed (needed for Gemini)")
        except Exception as e:
            if self.verbose:
                print(f"ℹ️  Gemini not available: {str(e)[:50]}")
        
        return None, None
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize LangChain tools."""
        return [
            Tool(
                name="flight_search",
                func=self._flight_search,
                description="Search flights. Input: JSON with source, destination, sort_by"
            ),
            Tool(
                name="hotel_search",
                func=self._hotel_search,
                description="Search hotels. Input: JSON with city, min_rating, max_price"
            ),
            Tool(
                name="weather_lookup",
                func=self._weather_lookup,
                description="Get weather forecast. Input: JSON with city, days"
            ),
            Tool(
                name="places_search",
                func=self._places_search,
                description="Find attractions. Input: JSON with city, type"
            ),
            Tool(
                name="budget_calculator",
                func=self._budget_calculator,
                description="Calculate budget. Input: JSON with prices and nights"
            )
        ]
    
    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create LangChain agent if LLM available."""
        if not self.llm:
            return None  # Demo mode
        
        template = """You are an expert Travel Planning Assistant. Create perfect trip itineraries.

Available tools:
{tools}

Tool Names: {tool_names}

Use this format:
Question: {input}
Thought: What should I do?
Action: tool name
Action Input: valid JSON
Observation: result
... (repeat as needed)
Thought: I have all info
Final Answer: Complete itinerary

Begin!
{agent_scratchpad}"""
        
        # Create a REACT-style agent for LangChain
        try:
            from langchain_experimental.agents import create_pandas_dataframe_agent
            from langchain_experimental.agents.agent_toolkits import create_react_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
            
            # Use create_react_agent for newer versions
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            agent = create_react_agent(self.llm, self.tools, prompt)
            
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                max_iterations=15,
                handle_parsing_errors=True
            )
        except ImportError:
            # Fallback to older approach if experimental modules not available
            from langchain import hub
            from langchain.agents import create_structured_chat_agent
            
            # Get the prompt from the hub
            prompt = hub.pull("hwchase17/structured-chat-agent")
            
            agent = create_structured_chat_agent(self.llm, self.tools, prompt)
            
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                max_iterations=15,
                handle_parsing_errors=True
            )
    
    # Tool implementations (simplified for demo)
    def _flight_search(self, input_str: str) -> str:
        """Search flights."""
        try:
            params = json.loads(input_str)
            return json.dumps({
                "status": "success",
                "flights": [{
                    "airline": "IndiGo",
                    "price": 4800,
                    "departure": "14:00",
                    "duration": "2h 30m"
                }]
            })
        except:
            return json.dumps({"status": "error"})
    
    def _hotel_search(self, input_str: str) -> str:
        """Search hotels."""
        try:
            return json.dumps({
                "status": "success",
                "hotels": [{
                    "name": "Sea View Resort",
                    "rating": 4.5,
                    "price_per_night": 3200,
                    "amenities": ["Pool", "WiFi"]
                }]
            })
        except:
            return json.dumps({"status": "error"})
    
    def _weather_lookup(self, input_str: str) -> str:
        """Get weather."""
        try:
            return json.dumps({
                "forecast": [
                    {"day": 1, "condition": "Sunny", "temp": 31},
                    {"day": 2, "condition": "Clear", "temp": 30}
                ]
            })
        except:
            return json.dumps({"status": "error"})
    
    def _places_search(self, input_str: str) -> str:
        """Find places."""
        try:
            return json.dumps({
                "places": [
                    {"name": "Baga Beach", "type": "Beach", "rating": 4.6},
                    {"name": "Fort Aguada", "type": "Heritage", "rating": 4.5}
                ]
            })
        except:
            return json.dumps({"status": "error"})
    
    def _budget_calculator(self, input_str: str) -> str:
        """Calculate budget."""
        try:
            params = json.loads(input_str)
            flight = params.get("flight_price", 4800)
            hotel = params.get("hotel_price", 3200)
            nights = params.get("nights", 3)
            daily = params.get("daily_expense", 800)
            
            total = flight + (hotel * nights) + (daily * nights)
            
            return json.dumps({
                "breakdown": {
                    "flight": flight,
                    "hotel": hotel * nights,
                    "daily": daily * nights,
                    "total": total
                }
            })
        except:
            return json.dumps({"status": "error"})
    
    def plan_trip(
        self,
        source: str,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float] = None,
        preferences: Optional[str] = None
    ) -> Dict:
        """
        Plan complete trip itinerary.
        Works in both AI mode and demo mode!
        """
        
        if self.provider == "demo":
            # Use rule-based planning (no AI needed)
            return self._demo_plan_trip(source, destination, start_date, end_date, budget)
        
        # Use AI agent
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        query = f"""Plan a {days}-day trip from {source} to {destination} 
from {start_date} to {end_date}."""
        
        if budget:
            query += f" Budget: ₹{budget}."
        if preferences:
            query += f" Preferences: {preferences}."
        
        query += " Provide complete itinerary with flights, hotels, weather, activities, and budget."
        
        try:
            result = self.agent.invoke({"input": query})
            return {
                "status": "success",
                "provider": self.provider,
                "itinerary": result["output"]
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": self.provider,
                "message": str(e)
            }
    
    def _demo_plan_trip(self, source, dest, start, end, budget) -> Dict:
        """Fallback demo planning (rule-based)."""
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        days = (end_dt - start_dt).days + 1
        
        itinerary = f"""
🌍 YOUR {days}-DAY TRIP TO {dest.upper()}
{'='*60}

✈️  FLIGHT: IndiGo - ₹4,800
    {source} → {dest} | 2h 30m

🏨 HOTEL: Sea View Resort - ₹3,200/night
    Rating: 4.5/5 | Beach access, Pool, WiFi

🌤️  WEATHER: Sunny, 28-32°C throughout trip

📅 ITINERARY:
"""
        
        activities = [
            "Beach relaxation & water sports",
            "Heritage sites & local culture",
            "Shopping & cuisine exploration",
            "Adventure activities",
            "Scenic tours & photography"
        ]
        
        for i in range(days):
            itinerary += f"\n   Day {i+1}: {activities[i % len(activities)]}"
        
        total = 4800 + (3200 * days) + (800 * days)
        
        itinerary += f"""

💰 BUDGET: ₹{total:,}
    Flight: ₹4,800
    Hotel: ₹{3200*days:,}
    Food/Activities: ₹{800*days:,}

{'='*60}
"""
        
        return {
            "status": "success",
            "provider": "demo",
            "itinerary": itinerary
        }


# ============================================================================
# Streamlit-Compatible Deployment Function
# ============================================================================

def create_streamlit_agent():
    """
    Create agent optimized for Streamlit deployment.
    Automatically uses best available LLM.
    """
    
    # Check if running on Streamlit Cloud
    is_streamlit_cloud = (
        os.getenv("STREAMLIT_SHARING_MODE") or 
        "streamlit" in sys.argv[0].lower()
    )
    
    if is_streamlit_cloud:
        print("☁️  Detected Streamlit Cloud - optimizing for deployment")
    
    agent = HybridTravelAgent(verbose=False)  # Less verbose for production
    
    return agent


# ============================================================================
# Main Demo
# ============================================================================

def main():
    """Demo the hybrid agent."""
    
    print("\n" + "="*70)
    print("🌍 HYBRID TRAVEL AGENT - Works Everywhere!")
    print("="*70)
    print("\n✨ Auto-detects best available LLM:")
    print("   • Ollama (local) → Best for development")
    print("   • Gemini (cloud) → Best for Streamlit deployment")
    print("   • Demo mode → Works without any LLM\n")
    print("="*70 + "\n")
    
    # Initialize agent
    agent = HybridTravelAgent()
    
    print(f"\n📍 Planning sample trip using: {agent.provider.upper()}")
    print("-" * 70)
    
    # Plan trip
    result = agent.plan_trip(
        source="Delhi",
        destination="Goa",
        start_date="2024-03-01",
        end_date="2024-03-04",
        budget=20000
    )
    
    if result["status"] == "success":
        print(f"\n✅ Trip planned successfully with {result['provider']}!")
        print("="*70)
        print(result["itinerary"])
        print("="*70)
    else:
        print(f"\n❌ Error: {result.get('message')}")
    
    print("\n\n📚 Deployment Guide:")
    print("-" * 70)
    print("Local Development:")
    print("  → Install Ollama: https://ollama.ai/download")
    print("  → Run: ollama serve && ollama pull llama3.2")
    print("  → This script will automatically use it!\n")
    
    print("Streamlit Cloud Deployment:")
    print("  → Get Gemini key: https://makersuite.google.com/app/apikey")
    print("  → Add to Streamlit secrets: GOOGLE_API_KEY")
    print("  → Deploy - it will automatically use Gemini!\n")
    
    print("No AI Available:")
    print("  → Works in demo mode automatically")
    print("  → Still produces complete itineraries")
    print("  → Perfect for testing!\n")
    
    print("="*70)
    print("🎉 This agent works EVERYWHERE - just deploy it!")


if __name__ == "__main__":
    main()