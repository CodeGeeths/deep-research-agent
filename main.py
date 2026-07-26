import gradio as gr

from research_manager import ResearchManager


async def chat(message: str, _history: list[dict]):
    """Stream research status updates, then the final report, into the chatbot."""
    transcript = ""
    async for update in ResearchManager().run(message):
        transcript += f"{update}\n\n"
        yield transcript


demo = gr.ChatInterface(
    fn=chat,
    title="Deep Research Agent",
    description="Ask a research question. A planner agent designs the web searches, a search "
    "agent runs them, a writer agent drafts the report, and a push notification is sent to your "
    "phone when it's done.",
    examples=[
        "Most popular AI agent frameworks in 2026",
        "Latest breakthroughs in solid-state batteries",
        "How is the AI regulation landscape evolving in the EU and US?",
    ],
)

if __name__ == "__main__":
    demo.launch()
