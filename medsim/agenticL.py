import os
import json
import torch
from typing import Literal, Union
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline, BitsAndBytesConfig

torch.cuda.empty_cache()

###############################################################################
# 1) Scenario Classes
###############################################################################
class Scenario:
    """
    Represents a single scenario from a JSON line in agentclinic_medqa.jsonl.
    {
      "OSCE_Examination": {
         "Objective_for_Doctor": "...",
         "Patient_Actor": {...},
         "Physical_Examination_Findings": {...},
         "Test_Results": {...},
         "Correct_Diagnosis": "..."
      }
    }
    """
    def __init__(self, scenario_dict):
        self.exam = scenario_dict["OSCE_Examination"]

    def diagnosis_information(self) -> str:
        return self.exam.get("Correct_Diagnosis", "")

    def patient_information(self) -> dict:
        return self.exam.get("Patient_Actor", {})

    def objective_for_doctor(self) -> str:
        return self.exam.get("Objective_for_Doctor", "")

    def physical_exams(self) -> dict:
        return self.exam.get("Physical_Examination_Findings", {})

    def test_results(self) -> dict:
        return self.exam.get("Test_Results", {})


class ScenarioLoader:
    """
    Loads multiple scenarios from .jsonl, each line is a scenario.
    """
    def __init__(self, filepath="agentclinic_medqa.jsonl"):
        self.scenarios = []
        with open(filepath, "r") as f:
            for line in f:
                data = json.loads(line.strip())
                self.scenarios.append(Scenario(data))
        self.num_scenarios = len(self.scenarios)

    def get_scenario(self, scenario_id: int) -> Scenario:
        return self.scenarios[scenario_id]


###############################################################################
# 2) Custom State Class
###############################################################################
from langgraph.graph import MessagesState

class OSCEState(MessagesState):
    """
    Extend the default MessagesState to track how many questions
    the doctor has asked so far. 
    - If we exceed 20, the doctor must produce a diagnosis or we end.
    """
    questions_asked: int = 0


###############################################################################
# 3) Models / Agents
###############################################################################
DOCTOR_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
PATIENT_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
MEASUREMENT_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
MODERATOR_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

def load_pipeline(model_id: str) -> HuggingFacePipeline:
    pipe = pipeline(
        "text-generation",
        model=model_id,
        device_map="auto",
        torch_dtype=torch.float16,
        max_new_tokens=128,
        temperature=0.0,
        do_sample=False,
    )
    return HuggingFacePipeline(pipeline=pipe)

doctor_agent = load_pipeline(DOCTOR_MODEL_ID)
patient_agent = load_pipeline(PATIENT_MODEL_ID)
measurement_agent = load_pipeline(MEASUREMENT_MODEL_ID)
moderator_agent = load_pipeline(MODERATOR_MODEL_ID)

###############################################################################
# 4) Utility Functions
###############################################################################
def compare_results(doctor_diag: str, correct_diag: str) -> str:
    """
    Use the moderator model to check correctness.
    """
    prompt = (
        f"Doctor said: {doctor_diag}\n"
        f"Correct diagnosis: {correct_diag}\n"
        "Respond ONLY 'Yes' if the doctor's final diagnosis is correct, otherwise 'No'."
    )
    raw_output = moderator_agent.invoke(prompt)
    raw_output_lower = raw_output.lower()
    return "yes" if "yes" in raw_output_lower else "no"

def save_conversation_log(conversation: list[str], scenario_id: int):
    filename = f"scenario_{scenario_id}_log.txt"
    with open(filename, "w") as f:
        for line in conversation:
            f.write(line + "\n")
    print(f"Saved conversation to {filename}")


###############################################################################
# 5) Multi-Agent Logic Nodes
###############################################################################
def doctor_logic(state: OSCEState, scenario: Scenario):
    """
    The Doctor uses scenario data in the prompt. 
    Each time the Doctor node runs, we increment 'questions_asked'.
    If we exceed 20, we forcibly produce a final diagnosis or end.
    """
    # 1) Increment the question count
    state["questions_asked"] = state.get("questions_asked", 0) + 1

    messages = state["messages"]
    doc_objective = scenario.objective_for_doctor()

    # Build conversation
    conversation_text = ""
    for msg in messages:
        if isinstance(msg, SystemMessage):
            conversation_text += f"[System]: {msg.content}\n"
        elif isinstance(msg, HumanMessage):
            conversation_text += f"[User]: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            conversation_text += f"[Assistant]: {msg.content}\n"

    # If we have already asked 20 questions, we must produce a final diagnosis
    questions_asked = state["questions_asked"]
    if questions_asked >= 20:
        # Force the doctor to do final diagnosis
        forced_msg = f"The doctor has asked {questions_asked} questions already. Provide final DIAGNOSIS READY: <diagnosis>."
        return {"messages": [AIMessage(content=forced_msg)]}

    prompt = (
        "You are a Doctor with short dialogue responses (1-3 sentences).\n"
        f"Objective: {doc_objective}\n"
        f"Number of Questions Asked So Far: {questions_asked}\n"
        "You can ask up to 20 questions total before making a diagnosis.\n"
        'If you need tests, say "REQUEST TEST: <test>".\n'
        'When sure, say "DIAGNOSIS READY: <diagnosis>".\n'
        f"Conversation:\n{conversation_text}\n"
    )

    response = doctor_agent.invoke(prompt)
    return {"messages": [AIMessage(content=response)]}


def patient_logic(state: OSCEState, scenario: Scenario):
    """
    The Patient references scenario's Patient_Actor to shape responses.
    """
    messages = state["messages"]
    pat_info = scenario.patient_information()

    # Summaries
    pat_demo = pat_info.get("Demographics", "")
    pat_hist = pat_info.get("History", "")

    conversation_text = ""
    for msg in messages:
        if isinstance(msg, AIMessage) or isinstance(msg, SystemMessage):
            conversation_text += f"[Doctor said]: {msg.content}\n"

    prompt = (
        "You are a Patient responding in 1-2 sentences.\n"
        f"Demographics: {pat_demo}\nHistory: {pat_hist}\n"
        f"Conversation:\n{conversation_text}\n"
    )
    response = patient_agent.invoke(prompt)
    return {"messages": [AIMessage(content=response)]}


def measurement_logic(state: OSCEState, scenario: Scenario):
    """
    If the Doctor requests a test, we look at scenario data and return it.
    """
    messages = state["messages"]
    test_data = scenario.test_results()

    last_msg = messages[-1].content.lower()
    test_name = ""
    if "request test:" in last_msg:
        # parse out test name
        test_name = last_msg.split("test:")[-1].strip()

    # We'll just dump all relevant test data for simplicity
    test_info_str = "RESULTS: normal"
    if isinstance(test_data, dict):
        test_info_str = "TEST DATA:\n" + json.dumps(test_data, indent=2)

    prompt = (
        f"Doctor requested test: {test_name}\n"
        f"Returning relevant data:\n{test_info_str}\n"
        "Answer in a single short sentence.\n"
    )

    response = measurement_agent.invoke(prompt)
    return {"messages": [AIMessage(content=response)]}


###############################################################################
# 6) Decision Logic
###############################################################################
def decision_logic(state: OSCEState) -> Literal["patient", "measurement", END]:
    """
    If the doctor says 'DIAGNOSIS READY', end.
    If 'REQUEST TEST:', go to measurement
    Else go to patient
    """
    last_msg = state["messages"][-1].content.lower()
    if "diagnosis ready" in last_msg:
        return END
    if "request test:" in last_msg:
        return "measurement"
    return "patient"


###############################################################################
# 7) Build the Workflow
###############################################################################
from langgraph.graph import StateGraph

def create_multi_agent_workflow(scenario: Scenario) -> StateGraph:
    def doc_node(state: OSCEState):
        return doctor_logic(state, scenario)

    def pat_node(state: OSCEState):
        return patient_logic(state, scenario)

    def meas_node(state: OSCEState):
        return measurement_logic(state, scenario)

    workflow = StateGraph(OSCEState)
    workflow.add_node("doctor", doc_node)
    workflow.add_node("patient", pat_node)
    workflow.add_node("measurement", meas_node)

    workflow.add_edge(START, "doctor")
    workflow.add_conditional_edges("doctor", decision_logic)
    workflow.add_edge("patient", "doctor")
    workflow.add_edge("measurement", "doctor")

    return workflow


###############################################################################
# 8) Main
###############################################################################
if __name__ == "__main__":
    loader = ScenarioLoader("agentclinic_medqa.jsonl")
    total_scenarios = loader.num_scenarios
    total_correct = 0

    for scenario_id in range(total_scenarios):
        scenario = loader.get_scenario(scenario_id)
        workflow = create_multi_agent_workflow(scenario)
        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer=checkpointer)

        initial_messages = [
            SystemMessage(content="You are a doctor diagnosing a patient. You can ask up to 20 questions total."),
            HumanMessage(content="Hello Doctor, I've been having some symptoms...")
        ]

        # Invoke
        state = app.invoke({"messages": initial_messages}, config={"configurable": {"thread_id": scenario_id}})
        conversation = state["messages"]

        # Collect logs
        conversation_log = []
        for idx, msg in enumerate(conversation):
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            line = f"{idx}. {role}: {msg.content}"
            print(line)
            conversation_log.append(line)

        # Evaluate final
        last_doctor_msg = conversation[-1].content
        correct_diag = scenario.diagnosis_information()
        # Compare
        verdict = compare_results(last_doctor_msg, correct_diag)
        if verdict == "yes":
            total_correct += 1
        print(f"Scenario {scenario_id}, verdict: {verdict.upper()}")

        # Save logs
        log_file = f"scenario_{scenario_id}.log"
        with open(log_file, "w") as f:
            for l in conversation_log:
                f.write(l + "\n")

    print(f"Finished {total_scenarios} scenarios. Correct = {total_correct}/{total_scenarios}.")