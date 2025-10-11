import os
import streamlit as st
from datetime import date
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate

# --- AWS Bedrock LLM Initialization ---
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Travel Itinerary Planner 🧳", page_icon="🌍", layout="centered")

st.title("🌍 AI Travel Itinerary Planner")
st.write("Plan your dream trip with an AI-generated, personalized day-by-day itinerary!")

# --- User Inputs ---
city = st.text_input("🏙️ Enter the city you plan to visit")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Start date", min_value=date.today())
with col2:
    end_date = st.date_input("📅 End date", min_value=start_date)

language = st.selectbox("🌐 Preferred language", ["English", "Spanish", "French", "Hindi", "Japanese", "Other"])
budget = st.selectbox("💰 Budget level", ["Backpacker", "Mid-range", "Luxury"])
interests = st.multiselect(
    "🎯 Choose your interests",
    ["Food", "Adventure", "History", "Culture", "Nature", "Shopping", "Photography", "Relaxation"]
)

# --- Button Trigger ---
if st.button("✨ Generate Itinerary"):
    if not city or not start_date or not end_date:
        st.warning("Please enter city and travel dates.")
    else:
        with st.spinner("Generating your itinerary... 🗺️"):
            # --- Create Prompt ---
            prompt_template = PromptTemplate(
                input_variables=["city", "start_date", "end_date", "interests", "budget", "language"],
                template="""
                Create a detailed, day-by-day travel itinerary for a trip to {city} from {start_date} to {end_date}.
                Traveler interests include: {interests}.
                Budget level: {budget}.
                Preferred language: {language}.

                Include:
                - Key attractions and activities each day
                - Recommended food or dining spots
                - Cultural tips or local phrases
                - Travel time suggestions
                - Local events or festivals if any
                - Short travel advice at the end
                """
            )

            formatted_prompt = prompt_template.format(
                city=city,
                start_date=start_date,
                end_date=end_date,
                interests=", ".join(interests) if interests else "General sightseeing",
                budget=budget,
                language=language
            )

            # --- Call the Claude model ---
            response = llm.invoke(formatted_prompt)

            # --- Display Results ---
            st.success(f"✅ Your {len(response.content.splitlines())//5}-day itinerary for {city} is ready!")
            st.markdown("### 🧳 Your Personalized Itinerary")
            st.markdown(response.content)

            # --- Optional Download ---
            st.download_button(
                label="📥 Download Itinerary as Text",
                data=response.content,
                file_name=f"{city}_itinerary.txt",
                mime="text/plain"
            )

# --- Footer ---
st.markdown("---")
st.caption("💡 Powered by AWS Bedrock (Claude 3 Sonnet) + LangChain + Streamlit | Built by [Your Name]")
