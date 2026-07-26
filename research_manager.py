from agents import OutputGuardrailTripwireTriggered, Runner, gen_trace_id, trace

from orchestrator_agent import orchestrator_agent
from writer_agent import ReportData

STATUS_MESSAGES = {
    "plan_searches": "Planning searches...",
    "run_web_search": "Searching the web...",
    "write_report": "Writing report...",
    "send_notification": "Sending push notification...",
}


class ResearchManager:
    async def run(self, query: str):
        """Run the deep research process, yielding status updates and the final report.

        Orchestration itself is delegated to `orchestrator_agent`: the planner, search, writer,
        and notification agents are exposed to it as tools, and the LLM decides the order and
        number of calls. This just streams that run's tool activity as status updates and pulls
        the final report out of the `write_report` tool's output.
        """
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id, metadata={"query": query}):
            yield f"Starting research. Trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            report: ReportData | None = None
            result = Runner.run_streamed(orchestrator_agent, query)
            try:
                async for event in result.stream_events():
                    if event.type != "run_item_stream_event":
                        continue

                    if event.name == "tool_called":
                        tool_name = event.item.tool_name
                        yield STATUS_MESSAGES.get(tool_name, f"Calling {tool_name}...")
                    elif event.name == "tool_output" and isinstance(event.item.output, ReportData):
                        report = event.item.output
            except OutputGuardrailTripwireTriggered:
                yield (
                    "The drafted report was blocked by the content safety guardrail and could "
                    "not be delivered. Try rephrasing your query."
                )
                return

            if report is None:
                raise RuntimeError("Orchestrator finished without producing a report")

            yield "Research complete."
            yield report.markdown_report
