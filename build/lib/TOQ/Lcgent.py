import gc
import time
from typing import Annotated, Literal

import torch
import transformers
from transformers import pipeline

# LangChain / LangGraph Imports
from langchain_huggingface import HuggingFacePipeline
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode


###############################################################################
# 1) DEFINE TOOLS (OPTIONAL)
###############################################################################
# Tools can be invoked by either the doctor or the patient if you wire them that way.
# Here are two example tools: one for requesting a test, another for fetching patient history.

@tool
def request_test(test_name: str) -> str:
    """
    Simulate requesting a test. 
    In a real scenario, you'd call an API or look up a database.
    """
    return f"Requested test: {test_name}. [Mocked result: normal]"

@tool
def patient_history() -> str:
    """
    Return a mock patient history.
    In practice, you might retrieve this from a database or file.
    """
    return (
        "Patient History:\n"
        "- Age: 62 years old\n"
        "- Known conditions: Hypertension, Type 2 Diabetes\n"
        "- Family history: Stroke, Parkinson's disease\n"
        "- Current symptoms: Double vision, difficulty climbing stairs, upper limb weakness"
    )

tools = [request_test, patient_history]


###############################################################################
# 2) CREATE TWO HUGGING FACE PIPELINES (DOCTOR AGENT & PATIENT AGENT)
###############################################################################
# For simplicity, we’ll use the same model ID for both.
# In a real scenario, you could use different models or distinct prompts.

DOCTOR_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"    # Example (requires a license)
PATIENT_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"  # Example (same or different model)

print("Loading doctor model pipeline...")
doctor_pipeline = pipeline(
    "text-generation",
    model=DOCTOR_MODEL_ID,
    device_map="auto",         # Use GPU if available
    torch_dtype=torch.float16,  # Adjust to your preference
    max_new_tokens=128,
    temperature=0.2,
    do_sample=False
)
doctor_agent = HuggingFacePipeline(pipeline=doctor_pipeline)

print("Loading patient model pipeline...")
patient_pipeline = pipeline(
    "text-generation",
    model=PATIENT_MODEL_ID,
    device_map="auto",
    torch_dtype=torch.float16,
    max_new_tokens=128,
    temperature=0.2,
    do_sample=False
)
patient_agent = HuggingFacePipeline(pipeline=patient_pipeline)


###############################################################################
# 3) DEFINE SYSTEM PROMPTS FOR DOCTOR & PATIENT
###############################################################################
# System instructions tell each agent how they should behave.

doctor_system_prompt = """\
You are Dr. Agent, a concise AI doctor. You respond ONLY in short dialogue (1-3 sentences).
- Always start your response with "Doctor:".
- You can request tests by writing "REQUEST TEST: <test>" on a separate line.
- Once ready for a final conclusion, say "DIAGNOSIS READY: <diagnosis>" and then stop.
- DO NOT restate the entire patient prompt, just ask questions or respond to the patient's statements.
"""

patient_system_prompt = """\
You are the Patient. You have double vision, difficulty climbing stairs, and upper limb weakness.
- You answer the doctor's questions truthfully, in short (1-2 sentences).
- Provide consistent details about your symptoms. 
- You may refer to your patient history if needed.
"""


###############################################################################
# 4) CREATE STATEGRAPH NODES (DOCTOR LOGIC & PATIENT LOGIC)
###############################################################################
def doctor_logic(state: MessagesState):
    """
    1) Gathers conversation so far
    2) Builds a prompt
    3) Invokes the doctor_agent (LLM)
    4) Returns the doctor's new message
    """
    messages = state["messages"]

    # Build a simple text prompt from the conversation
    # For the doctor, we embed the 'doctor_system_prompt' once at the beginning,
    # followed by the user/patient messages, plus the doctor's past messages.
    # Each message is labeled "User:" or "Assistant:" for consistency.
    prompt = "System:\n" + doctor_system_prompt + "\n\n"
    for msg in messages:
        if isinstance(msg, HumanMessage):
            prompt += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            prompt += f"Assistant: {msg.content}\n"

    # Invoke the doctor agent
    raw_output = doctor_agent.invoke(prompt)

    # The text-generation pipeline often returns a list with "generated_text" 
    if isinstance(raw_output, list) and len(raw_output) > 0:
        doctor_response = raw_output[0]["generated_text"]
    elif isinstance(raw_output, str):
        doctor_response = raw_output
    else:
        doctor_response = str(raw_output)

    return {"messages": [AIMessage(content=doctor_response)]}


def patient_logic(state: MessagesState):
    """
    1) Gathers conversation so far
    2) Builds a prompt
    3) Invokes the patient_agent (LLM)
    4) Returns the patient's new message
    """
    messages = state["messages"]

    # Build a prompt from the conversation
    prompt = "System:\n" + patient_system_prompt + "\n\n"
    for msg in messages:
        if isinstance(msg, HumanMessage):
            prompt += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            prompt += f"Assistant: {msg.content}\n"

    # Invoke the patient agent
    raw_output = patient_agent.invoke(prompt)

    if isinstance(raw_output, list) and len(raw_output) > 0:
        patient_response = raw_output[0]["generated_text"]
    elif isinstance(raw_output, str):
        patient_response = raw_output
    else:
        patient_response = str(raw_output)

    return {"messages": [AIMessage(content=patient_response)]}


###############################################################################
# 5) DEFINE THE "SHOULD END?" FUNCTION
###############################################################################
# We'll end the conversation if the doctor has made a diagnosis 
# by looking for "DIAGNOSIS READY:" in the last doctor message.

def conversation_should_end(state: MessagesState) -> Literal["patient", END]:
    last_msg = state["messages"][-1].content
    # If the doctor's message includes "DIAGNOSIS READY:", then end.
    if "DIAGNOSIS READY:" in last_msg:
        return END
    return "patient"  # otherwise, next node is "patient"


def conversation_should_return_to_doctor(state: MessagesState) -> Literal["doctor", END]:
    # The patient won't end the conversation. 
    # We always go back to the doctor after the patient speaks.
    return "doctor"


###############################################################################
# 6) BUILD THE LANGGRAPH WORKFLOW
###############################################################################
def build_multi_agent_workflow():
    workflow = StateGraph(MessagesState)

    # Create two nodes: "doctor" and "patient"
    workflow.add_node("doctor", doctor_logic)
    workflow.add_node("patient", patient_logic)

    # The conversation starts with the doctor
    workflow.add_edge(START, "doctor")
    # After the doctor speaks, decide if we should end or go to patient
    workflow.add_conditional_edges("doctor", conversation_should_end)
    # After the patient speaks, we go back to the doctor
    workflow.add_conditional_edges("patient", conversation_should_return_to_doctor)

    return workflow


###############################################################################
# 7) MAIN EXECUTION
###############################################################################
if __name__ == "__main__":
    gc.collect()
    torch.cuda.empty_cache()

    # Optionally pass any 4-bit or 8-bit quantization config if your model supports it.
    # For brevity, we skip that here.

    print("\n--- Building Multi-Agent Workflow ---")
    multi_agent_workflow = build_multi_agent_workflow()

    # Tools can be integrated, but for this example, we won't add them to separate nodes.
    # If you do want to incorporate tool usage, you can insert a ToolNode and 
    # conditional edges for when the doctor or patient calls them.

    print("\n--- Compiling Workflow with MemorySaver ---")
    checkpointer = MemorySaver()
    app = multi_agent_workflow.compile(checkpointer=checkpointer)

    # Initialize conversation:
    # For demonstration, let's place the system messages (the roles) as "HumanMessage"
    # so that the next node (doctor) sees them as user input. Or we can do them as SystemMessages.
    # We'll do one system prompt for each agent. The user might have "Patient details" to share.

    # Start messages: We'll pass the system instructions to each agent's "mental context"
    # by using them as SystemMessages in the initial state.
    # However, we also have them embedded in the logic functions as "prompt += doctor_system_prompt",
    # so passing them again might be partially redundant. We'll keep it minimal here.

    # For instance, let's start with a "Patient" message that sets the scenario.
    initial_messages = [
        HumanMessage(content="Patient: I am experiencing double vision and weakness in my arms and legs.")
    ]

    print("\n--- Invoking Workflow to Start the Conversation ---")
    # final_state = app.invoke({"messages": initial_messages}, config={"configurable": {"thread_id": 42})
    final_state = app.invoke(
                            {"messages": initial_messages},
                            config={"configurable": {"thread_id": 42}}
    )
    # Now let's see how the conversation progresses. The doc and patient should alternate
    # until the doc says "DIAGNOSIS READY:" in a message.
    # The conversation is stored in final_state["messages"].

    print("\n--- Final Conversation ---")
    for idx, message in enumerate(final_state["messages"]):
        role = "User" if isinstance(message, HumanMessage) else "Assistant"
        # Or we can do message.role if you prefer
        print(f"{idx}. {role}: {message.content}\n")

    print("Done.")