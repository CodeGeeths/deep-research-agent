from agents import Agent, ModelSettings, function_tool

from config import MODEL_NAME
from messenger import push


@function_tool
def send_push_notification(message: str) -> str:
    """
    Send a push notification to the user's phone.

    Args:
        message: A short, plain-text message (no markdown) to push to the phone.
    """
    push(message)
    return "Push notification sent"


INSTRUCTIONS = """
You are provided with the short summary of a research report. Turn it into a concise,
plain-text push notification (no markdown, under 200 characters) that captures the key
finding, then send it using your tool.
"""

notification_agent = Agent(
    name="Notification Agent",
    instructions=INSTRUCTIONS,
    tools=[send_push_notification],
    model=MODEL_NAME,
    model_settings=ModelSettings(tool_choice="required"),
)
