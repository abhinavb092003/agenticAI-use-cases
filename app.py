import subprocess
import sys
import os

# 1. THE "GHOST" & SQLITE FIX (Must be at the very top)
try:
    import pkg_resources
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools<82.0.0"])
    import pkg_resources

try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 2. ENVIRONMENT SETUP
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

st.title("🚀 My First Agentic AI")

company = st.text_input("Which company should I research?")

# 3. CONSOLIDATED LOGIC BLOCK
# We use a unique 'key' to avoid DuplicateElementId errors
if st.button("Launch Agent", key="primary_research_btn") and company:
    if not os.environ["GOOGLE_API_KEY"]:
        st.error("Please add your GOOGLE_API_KEY to Streamlit Secrets!")
        st.stop()

    # --- DEFINE THE BRAIN ---
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    
    # --- DEFINE THE TOOLS ---
    search_tool = TavilySearchTool(max_results=3)

    # --- DEFINE THE AGENT ---
    researcher = Agent(
        role='Market Researcher',
        goal=f'Find 3 facts about {company}',
        backstory='A helpful and concise research assistant.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        memory=False
    )

    # --- DEFINE THE TASK ---
    task = Task(
        description=f'Find news for {company} in 2026. Focus on recent developments.',
        expected_output='3 bullet points.',
        agent=researcher
    )

    # --- DEFINE THE CREW ---
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=True,
        memory=False,
        stream=True  
    )

    # --- EXECUTION & UI ---
    with st.status("🚀 Agent Workflow Active...", expanded=True) as status:
        st.write("🔍 Searching for latest news...")
        
        # Start streaming execution
        streaming_output = crew.kickoff()
        
        # Placeholder for the "typing" effect
        placeholder = st.empty()
        full_text = ""
        
        # Iterate over the chunks
        try:
            for chunk in streaming_output:
                # Safe access to content for different CrewAI versions
                content = getattr(chunk, 'content', str(chunk))
                full_text += content
                placeholder.markdown(full_text + "▌")
            
            # Final clean update
            placeholder.markdown(full_text)
            status.update(label="✅ Research Complete!", state="complete", expanded=False)
        
        except Exception as e:
            st.error(f"An error occurred during streaming: {e}")
