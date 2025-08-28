from langgraph.graph import StateGraph, END , START
from typing import TypedDict , Optional, Union, List
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))   

class practical_details(TypedDict):
    grade: str
    subject: str
    aim : str
    apparatus: str
    theory: str 
    observations: str
    procedure: str  
    codes : str
    code_output: str
    conclusion: str
    diagram: Optional[List[Union[str,bytes]]]
    file_combiner : str
    programming : bool
    selected_sections: List[str]

graph = StateGraph(practical_details)

def input_grade(state: practical_details):
    return state

def apparatus(state: practical_details):
    if "Apparatus" not in state["selected_sections"]:
        return {"apparatus": ""}
    prompt = f"List the apparatus required for a {state['aim']} practical in {state['subject']} for {state['grade']} students. Response should be comma separated."
    model = genai.GenerativeModel("gemini-2.5-flash")
    return {"apparatus": model.generate_content(prompt).text.strip()}

def theory(state: practical_details):
    if "Theory" not in state["selected_sections"]:
        return {"theory": ""}
    prompt = f"Provide a 120-word theory for a {state['aim']} practical in {state['subject']} for {state['grade']}."
    model = genai.GenerativeModel("gemini-2.5-flash")
    return {"theory": model.generate_content(prompt).text.strip()}

def procedure(state: practical_details):
    if "Procedure" not in state["selected_sections"]:
        return {"procedure": ""}
    prompt = f"List a clear step-by-step procedure for {state['aim']} in {state['subject']} ({state['grade']}). Use numbered steps(~150 words)."
    model = genai.GenerativeModel("gemini-2.5-flash")
    return {"procedure": model.generate_content(prompt).text.strip()}

def observations(state: practical_details):
    if "Observations" not in state["selected_sections"]:
        return {"observations": ""}
    if state.get("observations"):
        return {"observations": state["observations"]}
    prompt = f"Provide observations in a table format for {state['aim']} in {state['subject']} ({state['grade']})."
    model = genai.GenerativeModel("gemini-2.5-flash")
    return {"observations": model.generate_content(prompt).text.strip()}

def conclusion(state: practical_details):
    if "Conclusion" not in state["selected_sections"]:
        return {"conclusion": ""}
    prompt = f"Write a short conclusion (~50 words) for {state['aim']} in {state['subject']} ({state['grade']})."
    model = genai.GenerativeModel("gemini-2.5-flash")
    return {"conclusion": model.generate_content(prompt).text.strip()}

def codes(state: practical_details):
    if "Code" not in state["selected_sections"]:
        return {"codes": ""}
    if state["programming"]:
        if state["codes"]:  
            return {"codes": state["codes"]}
        prompt = f"Provide a simple program for {state['aim']}. Return only code without explanation."
        model = genai.GenerativeModel("gemini-2.5-flash")
        return {"codes": model.generate_content(prompt).text.strip()}
    return {"codes": ""}

def code_outputs(state: practical_details):
    if "Output" not in state["selected_sections"]:
        return {"code_output": ""}
    if state.get("code_output"):
        return {"code_output": state["code_output"]}
    if state["programming"]:
        prompt = f"Show a sample output for {state['codes']}. Return only raw terminal output."
        model = genai.GenerativeModel("gemini-2.5-flash")
        return {"code_output": model.generate_content(prompt).text.strip()}
    return {"code_output": ""}

def combine_file(state: practical_details):
    content = ""

    if "Aim" in state["selected_sections"]:
        content += f"<h2>Aim:</h2>\n<p>{state['aim']}</p>\n"

    if "Apparatus" in state["selected_sections"]:
        content += f"<h2>Apparatus:</h2>\n<p>{state['apparatus']}</p>\n"

    if "Theory" in state["selected_sections"]:
        content += f"<h2>Theory:</h2>\n<p>{state['theory']}</p>\n"

    if "Code" in state["selected_sections"]:
        content += f"<h2>Code:</h2>\n<pre>{state['codes']}</pre>\n"

    if "Output" in state["selected_sections"]:
        content += f"<h2>Output:</h2>\n<pre>{state['code_output']}</pre>\n"

    if "Procedure" in state["selected_sections"]:
        content += f"<h2>Procedure:</h2>\n<p>{state['procedure']}</p>\n"

    if "Observations" in state["selected_sections"]:
        content += f"<h2>Observations:</h2>\n<p>{state['observations']}</p>\n"

    if "Conclusion" in state["selected_sections"]:
        content += f"<h2>Conclusion:</h2>\n<p>{state['conclusion']}</p>\n"

    if "Diagrams" in state["selected_sections"] and state.get("diagram"):
        content += "\n<h2>Diagrams / Photos:</h2>\n"
        for i, _ in enumerate(state["diagram"], start=1):
            content += f"![Diagram {i}](Uploaded_Image_{i})\n"

    return {"file_combiner": content}

# Add nodes
graph.add_node("input_par", input_grade)
graph.add_node("apparatus", apparatus)
graph.add_node("theory", theory)
graph.add_node("procedure", procedure)
graph.add_node("observations", observations)
graph.add_node("conclusion", conclusion)
graph.add_node("codes", codes)
graph.add_node("code_outputs", code_outputs)
graph.add_node("combine_file", combine_file)

# Workflow edges
graph.add_edge(START, "input_par")
for node in ["apparatus", "theory", "procedure", "observations", "conclusion", "codes", "code_outputs"]:
    graph.add_edge("input_par", node)
    graph.add_edge(node, "combine_file")

graph.add_edge("combine_file", END)

workflow = graph.compile()
