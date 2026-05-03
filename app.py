import os
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 1. API SETUP
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

# 2. OPTIMIZED BRAIN
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1
)

# 3. OPTIMIZED TOOL
search_tool = TavilySearchTool(search_depth="basic", max_results=2)

st.set_page_config(page_title="Fast Agent Researcher", layout="centered")
st.title("🚀 Fast Agentic Researcher")

company = st.text_input("Enter Company Name:", placeholder="e.g. Nvidia")

# Create the placeholder OUTSIDE the button logic so it's ready to receive data
report_placeholder = st.empty()

if st.button("Run Fast Research", key="fast_btn") and company:
    # Immediate visual feedback
    st.toast(f"Starting research for {company}...")
    
    # Define Agent
    researcher = Agent(
        role='Swift Reporter',
        goal=f'Quickly summarize 3 facts about {company}',
        backstory='You are optimized for speed and brevity.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        memory=False
    )

    # Define Task
    task = Task(
        description=f'Quickly find 3 recent news bullet points about {company}.',
        expected_output='3 concise bullet points.',
        agent=researcher
    )

    # Define Crew
    crew = Crew(agents=[researcher], tasks=[task], stream=True)

    # 4. ADDRESSING THE "VISIBILITY" DEFECT
    with st.status("🔧 Agent is working...", expanded=True) as status:
        st.write("📡 Accessing Tavily search...")
        
        # Start streaming
        streaming_output = crew.kickoff()
        
        st.write("✍️ Drafting output...")
        full_text = ""
        
        # Use the placeholder created earlier (outside the status box)
        for chunk in streaming_output:
            # Handle chunk data safely
            content = getattr(chunk, 'raw', str(chunk)) # CrewAI 2026 uses .raw or str
            if hasattr(chunk, 'content'):
                content = chunk.content
            
            full_text += content
            # This updates the main webpage area, not just the status box
            report_placeholder.markdown(full_text + "▌")
        
        # Final cleanup
        report_placeholder.markdown(full_text)
        status.update(label="✅ Research Completed!", state="complete", expanded=False)

    st.success("Research finalized below.")
