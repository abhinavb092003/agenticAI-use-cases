# 1. THE SQLITE & SETTINGS PATCH (MUST BE AT THE VERY TOP)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
# Disable CrewAI telemetry to avoid configuration checks
os.environ["OTEL_SDK_DISABLED"] = "true" 
os.environ["PYDANTIC_SKIP_VALIDATOR_STRINGS"] = "true"

import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 2. Setup API Keys
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

# 3. Brain & Tool Initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

search_tool = TavilySearchTool()

st.title("🚀 Agentic Researcher v5.0")
company = st.text_input("Enter Company Name to Research:")

if st.button("Start Agents") and company:
    # 4. Define Agent (Explicitly disable everything that touches ChromaDB)
    researcher = Agent(
        role='Business Intelligence Specialist',
        goal=f'Summarize latest news for {company}',
        backstory='You are a master at gathering corporate data.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        memory=False # Critical
    )

    # 5. Define Task
    task = Task(
        description=f'Find 3 recent facts about {company}.',
        expected_output='A 3-point bulleted list.',
        agent=researcher
    )

    # 6. Launch
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        memory=False # Critical
    )
    
    with st.spinner("The Agent is thinking..."):
        try:
            result = crew.kickoff()
            st.success("Task Complete!")
            st.markdown(str(result.raw))
        except Exception as e:
            st.error(f"Execution Error: {e}")
