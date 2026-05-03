# 1. THE SQLITE PATCH (MUST BE AT THE VERY TOP)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import streamlit as st

# 2. Disable all background telemetry and memory checks
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["PYDANTIC_SKIP_VALIDATOR_STRINGS"] = "true"

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 3. Setup API Keys
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

# 4. Define the Brain (Flash is the best "Free" engine)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

st.title("🚀 My First AI Agent")

company = st.text_input("Enter a company to research:")

if st.button("Run Research") and company:
    # 5. Initialize the Tool inside the button click to save memory
    search_tool = TavilySearchTool()

    # 6. Define a SINGLE Agent (Simpler is better for the first run)
    researcher = Agent(
        role='Market Researcher',
        goal=f'Find 3 facts about {company}',
        backstory='A helpful AI assistant.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        memory=False
    )

    # 7. Define the Task
    task = Task(
        description=f'Search for news on {company}.',
        expected_output='3 bullet points.',
        agent=researcher
    )

    # 8. Define the Crew
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=True,
        memory=False
    )
    
    with st.spinner("Agent is working..."):
        try:
            result = crew.kickoff()
            st.success("Done!")
            st.markdown(result.raw)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
