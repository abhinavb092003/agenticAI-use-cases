import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"
os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_API_KEY"

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
search_tool=TavilySearchResults()
st.title("Free Agentic Proposal Researcher")
company=st.text_input("Enter Company Name to Research:")
if st.button("Generate Proposal Outline") and company:
    researcher = Agent(

        role='Business Researcher',
        goal=f'Find key challenges and recent news for {company}',
        backstory='Expert in corporate strategy and market analysis.',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

writer = Agent(
    role='Proposal Architect',
    goal='Create a high-level proposal outline based on research',
    backstory='Specialist in creating persuasive business cases.',
    llm=llm,
    verbose=True
)

task1=Task(description=f'Serach for {company}s mission and 2026 goals.', agent=researcher, expected_output="A summary of company goals.")
task2 = Task(description='Draft a 3-section proposal outline.', agent=writer, expected_output="A markdown formatted proposal outline.")
crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process = Process.sequential)
with st.spinner("Agents are working....."):
    result = crew.kickoff()
    st.markdown(results)




