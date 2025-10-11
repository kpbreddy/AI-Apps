import streamlit as st
import json
import requests
from datetime import datetime, timedelta
import openai  # or use anthropic if you prefer Claude

# ---- CONFIG ----
st.set_page_config(page_title="🧠 Personal Learning Path Generator", page_icon="🧭", layout="centered")

# Replace with your API key
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your_openai_api_key_here")

# Optional YouTube search function
def search_youtube(query, max_results=3):
    """Search YouTube for learning videos related to a topic"""
    YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", "your_youtube_api_key_here")
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "your_youtube_api_key_here":
        return []
    url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=playlist&q={query}&maxResults={max_results}"
        f"&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(url).json()
    results = []
    for item in response.get("items", []):
        title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/playlist?list={item['id']['playlistId']}"
        results.append({"title": title, "url": video_url})
    return results


# ---- APP TITLE ----
st.title("🧠 Personal Learning Path Generator")
st.markdown("Turn your goal into a concrete weekly learning roadmap — with optional real YouTube playlists.")

# ---- INPUT FORM ----
with st.form("learning_path_form"):
    current_skill = st.text_input("🎯 Current Skill", "Intermediate in Python")
    target_role = st.text_input("💼 Target Role", "Machine Learning Engineer")
    months = st.number_input("📅 Goal Timeframe (months)", 1, 24, 6)
    learning_style = st.selectbox("📘 Preferred Learning Style", ["Theory-focused", "Projects-focused", "Mixed (theory + projects)"])
    fetch_youtube = st.checkbox("🔗 Fetch real YouTube playlists for each topic", value=True)
    submitted = st.form_submit_button("🚀 Generate Learning Path")

# ---- GENERATION LOGIC ----
if submitted:
    with st.spinner("🧩 Generating your personalized roadmap..."):
        prompt = f"""
        You are an expert learning designer.
        Create a weekly roadmap to go from "{current_skill}" to "{target_role}" in {months} months.
        Include: 
        - Week number and focus
        - Learning objectives (2-3)
        - Recommended resources (courses, books)
        - One project idea
        Format your response as valid JSON with:
        {{
          "weeks_total": number,
          "weeks": [
            {{
              "week": 1,
              "focus": "...",
              "learning_objectives": ["...", "..."],
              "recommended_resources": [{{"type": "course", "title": "..."}}, {{...}}],
              "project_idea": "...",
              "search_keywords": ["...", "..."]
            }}
          ]
        }}
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI learning path creator."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )
            raw_output = response.choices[0].message.content.strip()
            # Clean and parse JSON
            json_start = raw_output.find("{")
            json_end = raw_output.rfind("}")
            json_data = json.loads(raw_output[json_start:json_end + 1])
        except Exception as e:
            st.error(f"Error parsing model output: {e}")
            st.code(raw_output)
            st.stop()

        # ---- DISPLAY LEARNING PATH ----
        st.success(f"✅ Generated {json_data.get('weeks_total', len(json_data['weeks']))} Weeks Plan!")
        for week in json_data["weeks"]:
            with st.expander(f"📘 Week {week['week']}: {week['focus']}"):
                st.write("**🎯 Learning Objectives:**")
                for obj in week["learning_objectives"]:
                    st.markdown(f"- {obj}")

                st.write("**📚 Recommended Resources:**")
                for r in week["recommended_resources"]:
                    st.markdown(f"- *{r['type'].capitalize()}*: **{r['title']}**")

                st.write("**💡 Project Idea:**")
                st.info(week["project_idea"])

                if fetch_youtube:
                    st.write("**🎥 YouTube Playlists:**")
                    for kw in week.get("search_keywords", []):
                        playlists = search_youtube(f"{kw} tutorial")
                        for p in playlists:
                            st.markdown(f"- [{p['title']}]({p['url']})")

        st.balloons()
