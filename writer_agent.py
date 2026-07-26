from agents import Agent, GuardrailFunctionOutput, OutputGuardrail, RunContextWrapper, Runner
from pydantic import BaseModel, Field

from config import MODEL_NAME

INSTRUCTIONS = """
You are a senior researcher tasked with writing a cohesive report for a research query.
You will be provided with the original query, and some research. Each piece of research may
include a "Sources:" list of markdown links it was drawn from.
Generate a comprehensive report based on the research and the query.
The final output should be in markdown format, and it should be lengthy and detailed. Aim
for 5-10 pages of content, at least 1000 words.

End the report with a "## Sources" section that lists every source link from the research,
deduplicated, as a markdown list. Do not invent links that were not provided in the research.
"""

SAFETY_INSTRUCTIONS = """
You are a content safety reviewer for a research report. Decide whether the report violates any
of the following:
- Contains inappropriate, hateful, harassing, or sexually explicit content
- Talks badly about, insults, or disparages a person, group, or organization
- Takes a gratuitously inflammatory or one-sided stance on a controversial topic (e.g. politics,
  religion) rather than neutrally reporting what sources say
- Exposes a private individual's sensitive personal information: home address, phone number,
  personal email, national ID / SSN / passport number, financial or medical details, private
  login credentials or API keys, or precise real-time location

Neutral, factual reporting on a controversial topic, including summarizing different sides of a
debate, is fine and should not be flagged. Information about public figures that is relevant to
the query and already widely publicly known (e.g. a politician's office address, a company
executive's professional role) is fine. Only flag genuine violations.
"""


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


class ContentSafetyCheck(BaseModel):
    is_flagged: bool = Field(description="True if the report violates the safety policy.")
    reasoning: str = Field(description="Brief explanation of the decision.")


content_safety_agent = Agent(
    name="Content Safety Checker",
    instructions=SAFETY_INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=ContentSafetyCheck,
)


async def report_content_guardrail_fn(
    ctx: RunContextWrapper, agent: Agent, output: ReportData
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        content_safety_agent,
        f"Short summary: {output.short_summary}\n\nReport:\n{output.markdown_report}",
        context=ctx.context,
    )
    check = result.final_output_as(ContentSafetyCheck)
    return GuardrailFunctionOutput(output_info=check, tripwire_triggered=check.is_flagged)


report_content_guardrail = OutputGuardrail(
    guardrail_function=report_content_guardrail_fn,
    name="report_content_guardrail",
)

writer_agent = Agent(
    name="Writer Agent",
    instructions=INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=ReportData,
    output_guardrails=[report_content_guardrail],
)
