__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Correct 2026 Import for CrewAI Tools
try:
    from crewai_tools import TavilySearchTool
except ImportError:
    st.error("Installation Error: Please ensure 'crewai-tools' is in your requirements.txt and reboot.")
    st.stop() # This prevents the NameError by stopping the script here

# 2. Setup API Keys
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "YOUR_KEY")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "YOUR_KEY")

# 3. Initialize the Brain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 4. Initialize the Tool (Using the correct 2026 class name)
search_tool = TavilySearchTool()

st.title("🚀 Agentic Researcher v3.3")
company = st.text_input("Enter Company Name:")

if st.button("Run Agents") and company:
    # 5. Define Agent
    researcher = Agent(
        role='Market Analyst',
        goal=f'Research {company} news',
        backstory='Expert researcher.',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

    # 6. Define Task
    task = Task(
        description=f'Find 3 facts about {company}.',
        expected_output='3 bullet points.',
        agent=researcher
    )

    # 7. Launch
    crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    
    with st.spinner("Agent is searching..."):
        result = crew.kickoff()
        st.markdown(str(result.raw))
