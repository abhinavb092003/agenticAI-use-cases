# 1. THE SQLITE PATCH (MUST BE AT THE VERY TOP)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass 

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 2. Setup API Keys
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

# 3. Define the Brain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 4. Initialize Tool
try:
    search_tool = TavilySearchTool()
except Exception as e:
    st.error(f"Tool Error: {e}")
    st.stop()

st.title("🚀 Agentic Researcher v4.0")
company = st.text_input("Enter Company Name:")

if st.button("Run Agents") and company:
    # 5. Define Agent
    researcher = Agent(
        role='Market Analyst',
        goal=f'Find 3 recent news facts about {company}',
        backstory='Expert researcher.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        memory=False # <--- EXPLICITLY DISABLE MEMORY HERE
    )

    # 6. Define Task
    task = Task(
        description=f'Search for the latest news on {company}.',
        expected_output='A bulleted list of 3 facts.',
        agent=researcher
    )

    # 7. Define the Crew (The "Manager")
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        memory=False # <--- EXPLICITLY DISABLE MEMORY HERE TOO
    )
    
    with st.spinner("Agent is working..."):
        try:
            result = crew.kickoff()
            st.markdown("### Research Results:")
            st.markdown(str(result.raw))
        except Exception as e:
            st.error(f"Execution Error: {e}")
