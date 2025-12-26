import streamlit as st
from datetime import datetime, timedelta
from src.agent.travel_agent import HybridTravelAgent
import os

# Page configuration
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


def check_gemini_key():
    """Placeholder for future API key checks (currently no front-end warning)."""
    return True


def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🌍 AI Travel Planning Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Note: Agent auto-detects best available LLM (Ollama/Gemini/Demo)
        st.info("🤖 Auto-detects best LLM: Ollama → Gemini → Demo")
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls creativity (higher = more creative)"
        )
        
        verbose = st.checkbox(
            "Show Reasoning Steps",
            value=False,
            help="Display agent's thinking process"
        )
    
    # Main form
    st.header("📋 Plan Your Trip")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source = st.text_input(
            "Source City",
            value="Delhi",
            placeholder="e.g., Delhi, Mumbai"
        )
        
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() + timedelta(days=7),
            min_value=datetime.now()
        )
        
        budget = st.number_input(
            "Budget (₹)",
            min_value=0,
            value=20000,
            step=1000
        )
    
    with col2:
        destination = st.text_input(
            "Destination City",
            value="Goa",
            placeholder="e.g., Goa, Bangalore"
        )
        
        end_date = st.date_input(
            "End Date",
            value=datetime.now() + timedelta(days=10),
            min_value=datetime.now()
        )
        
        preferences = st.text_input(
            "Preferences (optional)",
            placeholder="e.g., beach, heritage, adventure"
        )
    
    # Plan trip button
    if st.button("🚀 Plan My Trip", type="primary"):
        if not source or not destination:
            st.error("Please fill in source and destination cities!")
            return
        
        if end_date <= start_date:
            st.error("End date must be after start date!")
            return
        
        # Initialize agent
        with st.spinner("🤖 Initializing Travel Agent..."):
            try:
                agent = HybridTravelAgent(
                    temperature=temperature,
                    verbose=verbose
                )
            except Exception as e:
                st.error(f"Failed to initialize agent: {str(e)}")
                st.info("Make sure your API key is set in the environment or install Ollama locally.")
                return
        
        # Plan trip
        with st.spinner("📋 Planning your trip... This may take a minute."):
            try:
                result = agent.plan_trip(
                    source=source,
                    destination=destination,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    budget=budget if budget > 0 else None,
                    preferences=preferences if preferences else None
                )
                
                if result["status"] == "success":
                    st.success("✅ Trip planning completed!")
                    st.markdown("---")
                    
                    # Display itinerary
                    st.subheader("📅 Your Trip Itinerary")
                    st.markdown(result["itinerary"])
                    
                    # Show reasoning if enabled
                    if verbose and result.get("intermediate_steps"):
                        with st.expander("🤔 View Agent Reasoning"):
                            st.text("Agent reasoning steps would appear here when using AI mode")
                
                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error occurred')}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if "API" in str(e) or "key" in str(e).lower():
                    st.info("Please check your API key configuration or install Ollama locally.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Powered by LangChain & Multiple LLMs | AI Travel Planning Assistant"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

