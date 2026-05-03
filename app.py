import os
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import TavilySearchTool

# 1. API SETUP
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
os.environ["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY", "")

# 2. OPTIMIZED BRAIN (Speed focused)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", # Fastest 1.5 model
    temperature=0.1 # Forces concise, faster responses
)

# 1. OPTIMIZED TOOL (Corrected search_depth)
# 'basic' is the fastest valid option for this tool wrapper.
search_tool = TavilySearchTool(search_depth="basic", max_results=2)


st.title("🚀 Fast Agentic Researcher")
company = st.text_input("Enter Company Name:")

if st.button("Run Fast Research", key="fast_btn") and company:
    # Define Agent
    # Ensure the agent isn't over-thinking by keeping the goal simple.
    researcher = Agent(
        role='Swift Reporter',
        goal=f'Quickly summarize 3 facts about {company}',
        backstory='You are optimized for speed and brevity.',
        tools=[search_tool],
        llm=llm,
        verbose=True,
        memory=False
    )
    task = Task(
        description=f'Quickly find 3 recent news bullet points about {company}.',
        expected_output='3 concise bullet points.',
        agent=researcher
    )

    # Define Crew
    crew = Crew(agents=[researcher], tasks=[task], stream=True)

    # 4. ADDRESSING THE "STUCK" FEELING
    # Use st.status to show live background activity
    with st.status("🔧 Agent is starting work...", expanded=True) as status:
        st.write("📡 Connecting to Tavily Search...")
        
        # We use a placeholder for the live-typed text
        report_placeholder = st.empty()
        full_text = ""
        
        # Start streaming the output
        # This makes the app feel instant because text starts appearing immediately
        streaming_output = crew.kickoff()
        
        st.write("✍️ Drafting the summary...")
        for chunk in streaming_output:
            # Handle modern CrewAI chunk structure
            content = getattr(chunk, 'content', str(chunk))
            full_text += content
            report_placeholder.markdown(full_text + "▌") # Cursor effect
        
        # Clean up UI
        report_placeholder.markdown(full_text)
        status.update(label="✅ Research Completed!", state="complete", expanded=False)
