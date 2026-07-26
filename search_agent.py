from agents import Agent, ModelSettings, WebSearchTool

from config import MODEL_NAME

INSTRUCTIONS = """
You are a research assistant. Given a search term, you search the web for that term and
produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 words.
Capture the main points and be succinct. Reply only with the summary.
"""

search_agent = Agent(
    name="Search Agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
    model=MODEL_NAME,
    # Forced so every search actually hits the web; the SDK releases this
    # constraint again once the tool call has been made.
    model_settings=ModelSettings(tool_choice="required"),
)
