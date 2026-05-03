import subprocess
import sys

# 1. THE "GHOST" FIX
# This manually installs the missing library if the requirements.txt failed
try:
    import pkg_resources
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    import pkg_resources

# 2. THE SQLITE FIX
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import streamlit as st

# 3. DISABLE BACKGROUND NOISE
os.environ["OTEL_SDK_DISABLED"] = "true"

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 4. API SETUP
# Make sure these are in your Streamlit Secrets!
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

st.title("🚀 My First Agentic AI")

company = st.text_input("Which company should I research?")

if st.button("Launch Agent") and company:
    if not os.environ["GOOGLE_API_KEY"]:
        st.error("Please add your GOOGLE_API_KEY to Streamlit Secrets!")
        st.stop()

    # Define Brain
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    # Define Tool
    search_tool = TavilySearchTool(max_results=3)

    # Define Agent
    researcher = Agent(
        role='Market Researcher',
        goal=f'Find 3 facts about {company}',
        backstory='A helpful and concise research assistant.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        memory=False
    )

    # Define Task
    task = Task(
        description=f'Find news for {company} in 2026.',
        expected_output='3 bullet points.',
        agent=researcher
    )

  # 1. Define Crew with Streaming enabled
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=True,
        memory=False,
        stream=True  # Enables the streaming return type
    )

if st.button("Launch Agent"):
    # Create a status container to show the background steps
    with st.status("🚀 Agent Workflow Active...", expanded=True) as status:
        st.write("🔍 Searching for latest news...")
        
        # Start the streaming execution
        # kickoff() returns a streaming object we can iterate over
        streaming_output = crew.kickoff()
        
        # Create a placeholder for the "typing" effect below the status box
        placeholder = st.empty()
        full_text = ""
        
        # Iterate over the chunks as they arrive from Gemini
        for chunk in streaming_output:
            # In 2026, chunks have a .content attribute
            full_text += str(chunk.content)
            placeholder.markdown(full_text + "▌")
        
        # Final clean update (remove the cursor)
        placeholder.markdown(full_text)
        
        # Update the status bar to 'Complete'
        status.update(label="✅ Research Complete!", state="complete", expanded=False)
       
