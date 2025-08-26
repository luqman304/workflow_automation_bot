"""
Workflow Automation Bot — FastAPI
Endpoints:
- POST /summarize : executive summary of meeting notes
- POST /actions   : action items with owners and deadlines (heuristic)
- GET  /health    : health check
Optional: uses OpenAI if OPENAI_API_KEY is set; else rule-based fallback.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import os, re
from datetime import date, timedelta

app = FastAPI(title="Workflow Automation Bot")

class Notes(BaseModel):
    text: str

def rule_summary(text: str, max_sentences:int=5):
    # naive summarizer: choose top-N sentences by length & keywords
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences or sentences == ['']:
        return "No content provided."
    keywords = ['decide','action','risk','cost','revenue','timeline','deliverable','client','budget','scope','next','deadline']
    scored = []
    for s in sentences:
        score = len(s.split()) + sum(3 for k in keywords if k in s.lower())
        scored.append((score, s))
    top = [s for _, s in sorted(scored, reverse=True)[:max_sentences]]
    return "\n".join(top)

def rule_actions(text: str):
    lines = [l.strip("- *• ") for l in text.splitlines() if l.strip()]
    actions = []
    default_due = date.today() + timedelta(days=7)
    for l in lines:
        if any(k in l.lower() for k in ["todo","action","next","follow","send","draft","analyz","review","prepare","call","meet","email"]):
            owner = "Owner: " + ("You" if "we " in l.lower() else "Team")
            actions.append(f"- {l}  | {owner} | Due: {default_due.isoformat()}")
    if not actions:
        actions = ["- No explicit actions detected. Add 'Action:' or 'Next:' to lines for auto-detection."]
    return "\n".join(actions)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/summarize")
def summarize(notes: Notes):
    # Try OpenAI path
    try:
        from openai import OpenAI  # type: ignore
        key = os.getenv("OPENAI_API_KEY")
    except Exception:
        OpenAI = None
        key = None
    if OpenAI and key:
        client = OpenAI(api_key=key)
        prompt = f"Summarize the consulting meeting notes into a crisp executive summary (5 bullets max):\n\n{notes.text}"
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.2)
        return {"summary": resp.choices[0].message.content.strip()}
    # Fallback
    return {"summary": rule_summary(notes.text)}

@app.post("/actions")
def actions(notes: Notes):
    return {"actions": rule_actions(notes.text)}
