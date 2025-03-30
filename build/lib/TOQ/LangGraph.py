from typing import Literal, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
torch.cuda.empty_cache()
# ---- Tools Setup ----
@tool
def search(query: str):
    """Call to surf the web."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

tools = [search]
tool_node = ToolNode(tools)

# ---- Create a Hugging Face Model Pipeline ----
model_id = "meta-llama/Llama-3.1-8B-Instruct"

pipe = pipeline(
    "text-generation", 
    model=model_id, 
    device_map="auto",
    max_new_tokens=256,  # Ensures longer output
    temperature=0.0,     # Deterministic
    do_sample=False
)

model = HuggingFacePipeline(pipeline=pipe)

# ---- Graph Logic ----
def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Decides whether we should call a tool or end."""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: MessagesState):
    """Calls the Hugging Face pipeline with the assembled messages."""
    messages = state["messages"]

    # Build a simple prompt
    prompt = ""
    for msg in messages:
        if isinstance(msg, SystemMessage):
            prompt += f"System: {msg.content}\n"
        elif isinstance(msg, HumanMessage):
            prompt += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            prompt += f"Assistant: {msg.content}\n"
        else:
            prompt += f"{msg.role.capitalize()}: {msg.content}\n"

    # Invoke the model
    raw_output = model.invoke(prompt)

    # Parse the output
    if isinstance(raw_output, list) and len(raw_output) > 0:
        model_response = raw_output[0]["generated_text"]
    elif isinstance(raw_output, str):
        model_response = raw_output
    else:
        model_response = str(raw_output)

    return {"messages": [AIMessage(content=model_response)]}

# ---- Build the Graph ----
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# ---- Setup Memory and Compile ----
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# ---- Test the Workflow ----
final_state = app.invoke(
    {
        "messages": [
            SystemMessage(content="You are a research assistant. Respond concisely and accurately."),
            HumanMessage(content="What is the theory of scaling law in transformers")
        ]
    },
    config={"configurable": {"thread_id": 42}}
)

# Print the assistant's final response
print(final_state["messages"][-1].content)