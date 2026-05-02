__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
# NEW: Use the native CrewAI tool instead of the LangChain community one
from crewai_tools import TavilySearchResults

# 1. Setup API Keys (Use st.secrets on Streamlit Cloud)
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "YOUR_KEY")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "YOUR_KEY")

# 2. Define the Brain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 3. Define the Search Tool (Native version)
search_tool = TavilySearchResults()

st.title("🚀 Agentic Researcher v3.0")
company = st.text_input("Enter Company Name:")

if st.button("Run Agents") and company:
    # 4. Define Agents
    researcher = Agent(
        role='Market Research Analyst',
        goal=f'Provide a summary of {company} recent news',
        backstory='You are a detail-oriented corporate researcher.',
        tools=[search_tool], # This now passes the Pydantic check
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    writer = Agent(
        role='Business Writer',
        goal='Create a summary report',
        backstory='You turn data into clear business insights.',
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # 5. Define Tasks (expected_output is MANDATORY)
    task1 = Task(
        description=f'Find 3 recent facts about {company}.',
        expected_output='A list of 3 bullet points with news facts.',
        agent=researcher
    )

    task2 = Task(
        description='Summarize the research into a short paragraph.',
        expected_output='A 4-sentence summary paragraph.',
        agent=writer
    )

    # 6. Launch
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True
    )
    
    with st.spinner("Executing task..."):
        result = crew.kickoff()
        # In the latest CrewAI, result is an object. Get the raw text:
        st.markdown(str(result.raw))
