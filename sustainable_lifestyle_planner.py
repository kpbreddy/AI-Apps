import streamlit as st
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
import random

# --- Initialize LLM (AWS Bedrock) ---
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="🌱 Sustainable Lifestyle Planner",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- App Header ---
st.markdown("<h1 style='text-align: center; color: #2E8B57;'>🌱 Sustainable Lifestyle Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Create your personal eco-friendly plan for a greener life 🌎</p>", unsafe_allow_html=True)

# --- User Inputs ---
name = st.text_input("👤 Your Name", placeholder="e.g., Priya")
focus_areas = st.multiselect(
    "♻️ Choose your sustainability focus areas",
    ["Waste Reduction", "Eco-friendly Food Habits", "Energy Conservation", "Water Usage", "Sustainable Travel", "Minimalism", "Plastic-Free Living"]
)
plan_type = st.radio("🕒 Choose your plan type", ["Daily Plan", "Weekly Plan"])
goal_duration = st.slider("📅 Plan duration (weeks)", 1, 12, 4)
motivation_level = st.selectbox("💚 How motivated are you to change?", ["Just starting 🌱", "Getting serious 🌿", "Fully committed 🌳"])

# --- Background Color Rotation ---
bg_colors = ["#E8F5E9", "#F1F8E9", "#E3F2FD", "#FFF8E1", "#E0F7FA"]
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {random.choice(bg_colors)};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Generate Button ---
if st.button("🌍 Generate My Sustainability Plan"):
    if not name or not focus_areas:
        st.warning("Please enter your name and select at least one focus area.")
    else:
        with st.spinner("🌿 Crafting your personalized sustainability plan..."):
            # --- Prompt Template ---
            prompt_template = PromptTemplate(
                input_variables=["name", "focus_areas", "plan_type", "goal_duration", "motivation_level"],
                template="""
                Create a {plan_type} for {name}, focused on living a sustainable lifestyle.
                Areas of focus: {focus_areas}.
                Duration: {goal_duration} weeks.
                Motivation level: {motivation_level}.

                The plan should include:
                - Specific daily or weekly eco-friendly actions
                - Short, practical challenges
                - Motivation quotes or affirmations
                - A section called "Eco-Reflection" for journaling progress
                - One 'Hero Challenge' each week to push limits
                - End with a short summary called "Your Green Journey Ahead"
                Format with emojis and clear sections.
                """
            )

            # ✅ Fix here — precompute lowercase version
            plan_type_clean = plan_type.lower()

            formatted_prompt = prompt_template.format(
                name=name,
                focus_areas=", ".join(focus_areas),
                plan_type=plan_type_clean,
                goal_duration=goal_duration,
                motivation_level=motivation_level
            )

            response = llm.invoke(formatted_prompt)

            # --- Display Results ---
            st.success("✅ Your personalized sustainability plan is ready!")
            st.markdown("---")
            st.markdown(response.content)
            st.download_button(
                label="📥 Download Plan as Text",
                data=response.content,
                file_name=f"{name}_SustainabilityPlan.txt",
                mime="text/plain"
            )
