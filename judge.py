import os
import csv
from typing import TypedDict, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

load_dotenv()


# --- 1. State Definition ---
class GraphState(TypedDict):
    resume_text: str
    job_description: str
    reviewer_output: str
    feedback_history: List[str]
    status: str  # "PASS" or "FAIL"
    retry_count: int


# --- 2. Node Logic ---


class ResumeJudgeGraph:
    def __init__(self, model_name="gpt-4o-mini"):
        # Look for either key name
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAPI_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY (or OPENAPI_KEY) not found in environment variables."
            )

        self.llm = ChatOpenAI(model=model_name, temperature=0.4, api_key=api_key)

    def node_1_reviewer(self, state: GraphState):
        """
        Node 1: The Reviewer
        Analyzes resume vs JD. Adjusts based on feedback.
        """
        print(
            f"\n... Node 1 (Reviewer) is thinking (Attempt {state['retry_count'] + 1})..."
        )

        history_text = ""
        if state["feedback_history"]:
            history_text = (
                "\\n\\n--- PREVIOUS AUDITOR FEEDBACK (FIX THESE ISSUES) ---\\n"
            )
            for i, feedback in enumerate(state["feedback_history"]):
                history_text += f"Round {i+1} Feedback: {feedback}\\n"

        system_msg = """
        You are an Expert Technical Recruiter. 
        Your task is to evaluate a candidate's resume against a Job Description (JD).
        
        Output Requirements (PLEASE RESPOND IN THAI):
        1. Score (0-10): Be realistic but fair. Consider transferable skills.
        2. Analysis: Key strengths and gaps relative to the JD.
        3. Recommendation: Hire, Interview, or Reject.
        
        If you receive feedback from the Auditor, adjust your analysis. Focus on a balanced view—don't just list what's missing, but also what the candidate *can* bring to the table based on their background.
        """

        user_msg = f"""
        [JOB DESCRIPTION]
        {state['job_description']}

        [RESUME TEXT]
        {state['resume_text']}
        
        {history_text}
        
        Generate your evaluation now.
        """

        response = self.llm.invoke(
            [SystemMessage(content=system_msg), HumanMessage(content=user_msg)]
        )

        return {
            "reviewer_output": response.content,
            "retry_count": state["retry_count"] + 1,
        }

    def node_2_auditor(self, state: GraphState):
        """
        Node 2: The Auditor
        Checks Reviewer output against Resume and JD.
        """
        print("\n... Node 2 (Auditor) is verifying...")

        system_msg = """
        You are a Fair and Pragmatic Technical Auditor.
        Your goal is to ensure the Reviewer's evaluation is balanced and reasonable.
        
        Rules:
        1. Check for Accuracy: Ensure the Reviewer doesn't miss key skills that ARE in the resume.
        2. Check for Fairness: Did the Reviewer give an unfairly low score just because a specific keyword was missing, even if the candidate has highly relevant experience? 
        3. Transferable Skills: Encourage the Reviewer to consider if the candidate's background (e.g., general electrical design) translates well to the specific needs (e.g., MDB/DB).
        
        Output Format:
        - If the evaluation is fair and well-balanced: Return exactly "PASS".
        - If the evaluation is too harsh or missing obvious links: Return "FAIL: [Explain in THAI how to make the evaluation more balanced and fair]".
        """

        user_msg = f"""
        [JOB DESCRIPTION]
        {state['job_description']}

        [ORIGINAL RESUME TEXT]
        {state['resume_text']}
        
        [REVIEWER'S EVALUATION]
        {state['reviewer_output']}
        
        Verify this evaluation.
        """

        response = self.llm.invoke(
            [SystemMessage(content=system_msg), HumanMessage(content=user_msg)]
        )
        result = response.content.strip()

        status = "PASS" if result.upper() == "PASS" else "FAIL"

        # If fail, append to history
        new_history = state["feedback_history"]
        if status == "FAIL":
            print(f"!!! AUDITOR REJECTED: {result}")
            new_history = state["feedback_history"] + [result]
        else:
            print(f"\n>>> AUDITOR APPROVED <<<")

        return {"status": status, "feedback_history": new_history}

    def build_graph(self):
        workflow = StateGraph(GraphState)

        # Add Nodes
        workflow.add_node("reviewer", self.node_1_reviewer)
        workflow.add_node("auditor", self.node_2_auditor)

        # Set Entry Point
        workflow.set_entry_point("reviewer")

        # Add Edges
        workflow.add_edge("reviewer", "auditor")

        # Conditional Edge Logic
        def check_auditor_verdict(state: GraphState):
            if state["status"] == "PASS":
                return "end"
            if state["retry_count"] >= 3:
                print(
                    "\n*** Max retries reached. Returning last Reviewer output with warning. ***"
                )
                return "end"
            return "retry"

        workflow.add_conditional_edges(
            "auditor", check_auditor_verdict, {"end": END, "retry": "reviewer"}
        )

        return workflow.compile()


# Helper to load a resume from CSV
def load_resume_from_csv(csv_path, resume_id):
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == str(resume_id):
                return row["ocr_result"]
    return None


def main_evaluation_loop():
    # --- Configuration ---
    csv_db = "ocr_results.csv"
    output_csv = "judge_results.csv"
    jd_file = "job_description.txt"

    # 1. Load JD
    if os.path.exists(jd_file):
        with open(jd_file, "r", encoding="utf-8") as f:
            job_description = f.read()
    else:
        print(f"Error: {jd_file} not found.")
        return

    # 2. Check Input Data
    if not os.path.exists(csv_db):
        print(f"Error: {csv_db} not found. Please run OCR.py first.")
        return

    # 3. Setup Graph
    judge_graph = ResumeJudgeGraph()
    app = judge_graph.build_graph()

    # 4. Prepare Output CSV
    file_exists = os.path.exists(output_csv)
    with open(output_csv, mode="a", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        if not file_exists:
            writer.writerow(["id", "resumename", "score", "status", "evaluation"])

        # 5. Process all resumes
        with open(csv_db, mode="r", encoding="utf-8") as in_f:
            reader = csv.DictReader(in_f)
            import re

            def extract_score(text):
                # Try to find "Score (0-10): X" or "คะแนน: X"
                match = re.search(
                    r"(?:Score|คะแนน)\s*(?:\(0-10\))?:\s*(\d+(\.\d+)?)",
                    text,
                    re.IGNORECASE,
                )
                if match:
                    return match.group(1)
                return "N/A"

            for row in reader:
                resume_id = row["id"]
                resume_name = row["resumename"]
                resume_text = row["ocr_result"]

                print(f"\n>>> Processing ID {resume_id}: {resume_name}")

                initial_state = {
                    "resume_text": resume_text,
                    "job_description": job_description,
                    "reviewer_output": "",
                    "feedback_history": [],
                    "status": "START",
                    "retry_count": 0,
                }

                try:
                    final_state = app.invoke(initial_state)

                    evaluation_text = final_state["reviewer_output"]
                    score = extract_score(evaluation_text)
                    status = final_state["status"]

                    writer.writerow(
                        [resume_id, resume_name, score, status, evaluation_text]
                    )
                    out_f.flush()  # Save progress immediately

                    print(f"Done. Score: {score}")

                except Exception as e:
                    print(f"Error evaluating ID {resume_id}: {e}")

    print(f"\nEvaluation completed. Results saved to {output_csv}")


if __name__ == "__main__":
    main_evaluation_loop()
