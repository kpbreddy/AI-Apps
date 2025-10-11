import streamlit as st
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
import random

# --- Initialize LLM (Claude via Bedrock) ---
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)

# --- App Setup ---
st.set_page_config(page_title="🧘 Mindful Morning Coach", layout="centered")

# --- Mood-based Color Palettes ---
mood_colors = {
    "Calm": "#B3E5FC",
    "Stressed": "#FFE0B2",
    "Grateful": "#C8E6C9",
    "Motivated": "#FFF59D",
    "Tired": "#E1BEE7",
    "Reflective": "#FFCCBC",
}

# --- Background Randomizer for Variety ---
backgrounds = [
    "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
    "linear-gradient(135deg, #c3cfe2 0%, #c3f0ca 100%)",
    "linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)",
    "linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)",
]

bg_choice = random.choice(backgrounds)
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg_choice};
        color: #333333;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title Section ---
st.title("🧘 Mindful Morning Coach")
st.subheader("Start your day with calm, focus, and intention 🌞")
st.write("Tell me how you feel and what you want to focus on today.")

# --- User Inputs ---
mood = st.selectbox(
    "💭 How are you feeling right now?",
    ["Calm", "Stressed", "Grateful", "Motivated", "Tired", "Reflective"]
)

goals = st.text_input("🎯 What’s your focus or goal for today?", placeholder="e.g., stay positive, finish a key task, be present")
time_of_day = st.selectbox(
    "⏰ Time of day",
    ["Morning", "Afternoon", "Evening"]
)

# --- Background Color Based on Mood ---
if mood:
    color = mood_colors.get(mood, "#FFFFFF")
    st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:10px;'></div>", unsafe_allow_html=True)

# --- Button ---
if st.button("🌸 Get My Mindful Note"):
    if not mood or not goals:
        st.warning("Please select your mood and enter your goal for the day.")
    else:
        with st.spinner("Breathing in calm energy... ✨"):
            # --- Prompt ---
            prompt_template = PromptTemplate(
                input_variables=["mood", "goals", "time_of_day"],
                template="""
                You are a warm, empathetic mindfulness coach.
                Based on the user's current mood ({mood}), daily goal ({goals}), and time of day ({time_of_day}),
                write a short, inspiring reflection to start their day.

                Include:
                1. A personalized affirmation (1 line)
                2. A short mindfulness reflection (2–3 lines)
                3. A journaling prompt (1 question)

                Use a gentle, encouraging tone. Add fitting emojis.
                """
            )

            formatted_prompt = prompt_template.format(
                mood=mood, goals=goals, time_of_day=time_of_day
            )

            # --- Generate Response ---
            response = llm.invoke(formatted_prompt)

            # --- Display Output ---
            st.markdown("### 🌤️ Your Mindful Moment")
            st.write(response.content)

            # --- Optional Download ---
            st.download_button(
                label="📥 Save Reflection",
                data=response.content,
                file_name=f"mindful_note_{time_of_day.lower()}.txt",
                mime="text/plain"
            )

# --- Footer ---
st.markdown("---")
st.caption("🌼 Created with love using AWS Bedrock (Claude 3 Sonnet) + Streamlit | By [Your Name]")
