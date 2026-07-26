from agents import Agent

from config import MODEL_NAME
from notification_agent import notification_agent
from planner_agent import planner_agent
from search_agent import search_agent
from writer_agent import writer_agent

INSTRUCTIONS = """
You are the lead research agent. You answer the user's research query by orchestrating a team of
specialist tools yourself, deciding what to call and when. Work through the query like this:

1. Call `plan_searches` with the user's query to get a set of planned web searches.
2. Call `run_web_search` once per planned search (one search term at a time), passing the search
   term and the reason it was chosen. Run as many of these as the plan calls for.
3. Once you have gathered the search summaries, call `write_report` with the original query and
   all the collected summaries to produce the final markdown report.
4. Call `send_notification` with the report's short summary so the user is alerted that the report
   is ready.

Do not skip a step, and do not call `write_report` until you have the search summaries, or
`send_notification` until you have the written report.
"""

orchestrator_agent = Agent(
    name="Orchestrator Agent",
    instructions=INSTRUCTIONS,
    model=MODEL_NAME,
    tools=[
        planner_agent.as_tool(
            tool_name="plan_searches",
            tool_description=(
                "Given the user's research query, plan a set of web searches (each with a "
                "reason) that will best answer it."
            ),
        ),
        search_agent.as_tool(
            tool_name="run_web_search",
            tool_description=(
                "Search the web for a single search term and reason, returning a concise "
                "summary of the results."
            ),
        ),
        writer_agent.as_tool(
            tool_name="write_report",
            tool_description=(
                "Given the original query and the collected search summaries, write the final "
                "long-form markdown research report."
            ),
            # Let a tripped content guardrail raise instead of being swallowed into a generic
            # tool-error string the orchestrator might just retry past.
            failure_error_function=None,
        ),
        notification_agent.as_tool(
            tool_name="send_notification",
            tool_description=(
                "Given a short summary of the finished report, compose and send a push "
                "notification to the user's phone."
            ),
        ),
    ],
)
