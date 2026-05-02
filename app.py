__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

# SAFE IMPORT BLOCK
try:
    from crewai_tools import TavilySearchResultsTool as TavilyTool
except ImportError:
    try:
        from crewai_tools import TavilySearchResults as TavilyTool
    except ImportError:
        st.error("Could not find Tavily tool in crewai_tools. Check logs.")

# 1. Setup API Keys
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "YOUR_KEY")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "YOUR_KEY")

# 2. Define the Brain (Gemini 1.5 Flash)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 3. Initialize the Tool
search_tool = TavilyTool()

st.title("🚀 Agentic Researcher v3.2")
company = st.text_input("Enter Company Name:")

if st.button("Run Agents") and company:
    # 4. Define the Agent
    researcher = Agent(
        role='Corporate Strategic Researcher',
        goal=f'Find 3 critical news facts about {company} in 2026',
        backstory='Expert at finding non-obvious business trends.',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

    # 5. Define the Task
    task = Task(
        description=f'Search for news regarding {company}. Focus on 2026 goals.',
        expected_output='A bulleted list of 3 specific facts.',
        agent=researcher
    )

    # 6. Launch the Crew
    crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    
    with st.spinner("Agent is working..."):
        result = crew.kickoff()
        # In modern CrewAI, we use .raw to display the output string
        st.markdown("### Agent Output:")
        st.markdown(str(result.raw))
