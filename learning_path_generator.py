# learning_path_generator.py
import os
import json
import math
import requests
import streamlit as st
from datetime import date
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate

# ---------------------------
# Configuration / LLM Setup
# ---------------------------
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
BEDROCK_REGION = "us-east-1"

llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    region_name=BEDROCK_REGION
)

# ---------------------------
# Helper: YouTube Search (optional)
# ---------------------------
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # set this if you want playlist lookups

def search_youtube_playlists(query, max_results=3):
    """
    Searches YouTube for playlists matching `query`.
    Requires environment variable YOUTUBE_API_KEY to be set.
    Returns list of dicts: {title, url}
    """
    if not YOUTUBE_API_KEY:
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "playlist",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        js = r.json()
        results = []
        for item in js.get("items", []):
            playlist_id = item["id"].get("playlistId")
            title = item["snippet"].get("title")
            if playlist_id:
                results.append({
                    "title": title,
                    "url": f"https://www.youtube.com/playlist?list={playlist_id}"
                })
        return results
    except Exception as e:
        # return empty list on any error
        return []

# ---------------------------
# Prompt Template
# ---------------------------
roadmap_prompt = PromptTemplate(
    input_variables=["current_skill", "target_role", "months", "learning_style"],
    template="""
You are an expert learning coach and curriculum designer.

Produce a WEEK-BY-WEEK learning roadmap to go from the user's current skill to the target role within {months} months.
The user currently has: {current_skill}
The target role: {target_role}
Preferred learning style: {learning_style} (examples: project-first, theory-first, mixed, hands-on)

OUTPUT FORMAT: respond only with valid JSON (no additional commentary) that matches this structure:

{{
  "weeks_total": <int>,
  "weeks": [
    {{
      "week": <int>,
      "focus": "<short title>",
      "learning_objectives": ["...","..."],
      "recommended_resources": [
         {{ "type": "book|course|article|playlist|video", "title": "...", "note": "... (optional)" }}
      ],
      "project_idea": "<one-sentence project idea>",
      "search_keywords": ["keyword1","keyword2"]  // keywords to search YouTube or courses
    }},
    ...
  ],
  "meta": {{
    "assessment_checkpoints": ["e.g., build X, pass Y test"],
    "final_project": "Short description of a capstone project to demonstrate learning"
  }}
}}

Make the plan realistic and practical. Aim for weekly milestones, concrete projects, and a mix of fundamentals and applied work.
"""
)

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="🧠 Personal Learning Path Generator", layout="centered")
st.title("🧠 Personal Learning Path Generator")
st.write("Turn your goal into a concrete weekly learning roadmap. Optionally fetch real YouTube playlists for each week's keywords.")

with st.form("inputs"):
    current_skill = st.text_input("Current skill (e.g., Intermediate in Python)", value="Intermediate in Python")
    target_role = st.text_input("Target role (e.g., Machine Learning Engineer)", value="Machine Learning Engineer")
    months = st.number_input("Goal timeframe (months)", min_value=1, max_value=24, value=6)
    learning_style = st.selectbox("Preferred learning style", ["Mixed (theory + projects)", "Project-first", "Theory-first", "Hands-on (labs & exercises)"])
    include_youtube = st.checkbox("🔎 Also search YouTube playlists for each week's keywords (requires YOUTUBE_API_KEY env var)", value=False)
    submitted = st.form_submit_button("Generate Learning Roadmap")

if submitted:
    # Basic validation
    if not current_skill.strip() or not target_role.strip():
        st.error("Please provide your current skill and target role.")
    else:
        with st.spinner("Designing your roadmap..."):
            # Generate the prompt and call the LLM
            prompt_text = roadmap_prompt.format(
                current_skill=current_skill,
                target_role=target_role,
                months=months,
                learning_style=learning_style
            )

            try:
                response = llm.invoke(prompt_text)
                raw = response.content.strip()
            except Exception as e:
                st.error(f"LLM call failed: {e}")
                raw = None

        if not raw:
            st.error("No response from LLM.")
        else:
            # Try parse JSON
            parsed = None
            try:
                parsed = json.loads(raw)
            except Exception:
                # Sometimes LLM adds backticks or explanation — try to extract the JSON block
                try:
                    start = raw.index("{")
                    end = raw.rindex("}") + 1
                    json_text = raw[start:end]
                    parsed = json.loads(json_text)
                except Exception as e:
                    parsed = None

            if not parsed:
                st.warning("Could not parse JSON from model output. Showing raw output below — you can copy it and try again.")
                st.code(raw, language="json")
            else:
                # Display summary
                weeks_total = parsed.get("weeks_total") or len(parsed.get("weeks", []))
                st.success(f"Generated a {weeks_total}-week learning roadmap to become a **{target_role}**.")
                st.markdown("### 📋 Roadmap Overview")
                meta = parsed.get("meta", {})
                if meta:
                    st.markdown("**Assessment checkpoints:**")
                    for chk in meta.get("assessment_checkpoints", []):
                        st.write(f"- {chk}")
                    st.markdown("**Final project:**")
                    st.write(meta.get("final_project", "—"))

                st.markdown("---")
                # Render each week in an expander
                for w in parsed.get("weeks", []):
                    week_num = w.get("week")
                    with st.expander(f"Week {week_num}: {w.get('focus')}"):
                        st.markdown("**Learning objectives**")
                        for obj in w.get("learning_objectives", []):
                            st.write(f"- {obj}")

                        st.markdown("**Recommended resources**")
                        for res in w.get("recommended_resources", []):
                            typ = res.get("type", "resource")
                            title = res.get("title", "")
                            note = res.get("note", "")
                            line = f"- {title} ({typ})"
                            if note:
                                line += f" — {note}"
                            st.write(line)

                        st.markdown("**Project idea**")
                        st.write(w.get("project_idea", "—"))

                        # Optionally search YouTube
                        if include_youtube:
                            # choose a primary keyword (first in list)
                            keywords = w.get("search_keywords", [])
                            if keywords:
                                kw = keywords[0]
                                st.markdown(f"**YouTube playlists for:** `{kw}`")
                                playlists = search_youtube_playlists(kw, max_results=3)
                                if playlists:
                                    for p in playlists:
                                        st.write(f"- [{p['title']}]({p['url']})")
                                else:
                                    st.write("_No playlists found / API key missing or API error._")
                            else:
                                st.write("_No search keywords provided for this week._")

                # Download button — export cleaned JSON or text
                st.markdown("---")
                st.download_button(
                    label="📥 Download roadmap (JSON)",
                    data=json.dumps(parsed, indent=2),
                    file_name=f"learning_roadmap_{target_role.replace(' ','_')}.json",
                    mime="application/json"
                )

                # Also provide a friendly text summary
                def roadmap_to_text(parsed):
                    lines = []
                    lines.append(f"Learning Roadmap — {target_role} in {months} months\n")
                    lines.append("Assessment checkpoints:\n")
                    for chk in parsed.get("meta", {}).get("assessment_checkpoints", []):
                        lines.append(f"- {chk}")
                    lines.append("\nWeeks:\n")
                    for w in parsed.get("weeks", []):
                        lines.append(f"Week {w.get('week')}: {w.get('focus')}")
                        for obj in w.get("learning_objectives", []):
                            lines.append(f"  - {obj}")
                        lines.append(f"  Project: {w.get('project_idea')}")
                        lines.append("")
                    lines.append("\nFinal project:\n")
                    lines.append(parsed.get("meta", {}).get("final_project", "—"))
                    return "\n".join(lines)

                text_blob = roadmap_to_text(parsed)
                st.download_button(
                    label="📥 Download roadmap (text)",
                    data=text_blob,
                    file_name=f"learning_roadmap_{target_role.replace(' ','_')}.txt",
                    mime="text/plain"
                )

# ---------------------------
# Footer / Tips
# ---------------------------
st.markdown("---")
st.caption("Tip: For YouTube playlist lookup, set environment variable YOUTUBE_API_KEY and check the 'Also search YouTube' box. The app will use week's `search_keywords` to find relevant playlists.")
