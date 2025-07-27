



import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, tool
from agents.run import RunConfig
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents import AsyncOpenAI


try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",  
    openai_client=client
)

run_config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)

# ---------- ✅ Define Tools as Functions ----------


# class country_info(BaseModel):
#     country: str








@function_tool
# (name_override='capital', description_override= "hello")
def get_capital( country: str) -> str:
    """Given a country, return its capital city."""
    capitals = {
        "pakistan": "Islamabad",
        "india": "New Delhi",
        "france": "Paris",
        "germany": "Berlin",
        "japan": "Tokyo",
        "usa": "Washington D.C."
    }
    return capitals.get(country.lower(), "Sorry, I don't know the capital of that country.")

@function_tool
def get_language(country: str) -> str:
    """Given a country, return its official language."""
    languages = {
        "pakistan": "Urdu",
        "india": "Hindi",
        "france": "French",
        "germany": "German",
        "japan": "Japanese",
        "usa": "English"
    }
    return languages.get(country.lower(), "Sorry, I don't know the language of that country.")

@function_tool
def get_population(country: str) -> str:
    """Given a country, return its approximate population."""
    populations = {
        "pakistan": "240 million",
        "india": "1.4 billion",
        "france": "67 million",
        "germany": "83 million",
        "japan": "125 million",
        "usa": "331 million"
    }
    return populations.get(country.lower(), "Sorry, I don't know the population of that country.")

# ---------- ✅ Orchestrator Agent ----------

orchestrator = Agent(
    name="Country Info Bot",
    model=model,
    tools=[get_capital, get_language, get_population],
    instructions="""
You are a world knowledge expert. 
Given a country name, return:
1. The capital city
2. The official language
3. The approximate population

Use your tools to get the answers.
Return a clean, readable response.
"""
)

# ---------- ✅ Streamlit UI ----------

st.set_page_config(page_title="Country Info Bot", layout="centered")
st.title("🌍 Country Info Toolkit")

country_input = st.text_input("Enter a country name:")

if st.button("Get Info") and country_input.strip() != "":
    with st.spinner("Getting country information..."):
        try:
            result = Runner.run_sync(orchestrator, country_input, run_config=run_config)
            st.markdown("### 📌 Country Information")
            st.markdown(result.final_output)
        except Exception as e:
            st.error(f"❌ Error: {e}")



# asyncio.run(main())