__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

# The correct import name for the CrewAI-specific tool
try:
    from crewai_tools import TavilySearchResultsTool as TavilyTool
except ImportError:
    # Fallback in case of naming variations in different versions
    from crewai_tools import TavilySearchResults as TavilyTool

# 1. Setup API Keys
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "YOUR_KEY")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "YOUR_KEY")

# 2. Define the Brain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 3. Define the Search Tool correctly
search_tool = TavilyTool()

st.title("🚀 Agentic Researcher v3.1")
company = st.text_input("Enter Company Name:")

if st.button("Run Agents") and company:
    # 4. Define Agent
    researcher = Agent(
        role='Market Research Analyst',
        goal=f'Find 3 recent news facts about {company}',
        backstory='You are a detail-oriented corporate researcher.',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

    # 5. Define Task
    task = Task(
        description=f'Search for the latest news on {company}.',
        expected_output='A bulleted list of 3 recent news items.',
        agent=researcher
    )

    # 6. Launch
    crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    
    with st.spinner("Agent is searching the web..."):
        result = crew.kickoff()
        st.markdown(str(result.raw))
