import os
import streamlit as st
from gtts import gTTS
from tempfile import NamedTemporaryFile
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -------------------------------
# Initialize GPT LLM
# -------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-5", api_key=OPENAI_API_KEY)

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🎙️ Speech Generator with Voice (GPT + gTTS)")

topic = st.text_input("Enter your topic:")

if topic:
    # Step 1: Generate Title
    title_prompt = PromptTemplate(
        input_variables=["topic"],
        template=(
            "You are an experienced speech writer. "
            "Craft an impactful, memorable title for a speech on this topic: {topic}. "
            "Answer with one short, powerful title only."
        ),
    )
    title_chain = title_prompt | llm | StrOutputParser()
    title_result = title_chain.invoke({"topic": topic})
    st.subheader("🪶 Speech Title")
    st.write(title_result)

    # Step 2: Generate Speech
    speech_prompt = PromptTemplate(
        input_variables=["title"],
        template=(
            "Write a powerful, emotional, and inspiring 350-word speech "
            "for this title: {title}. Keep it conversational and motivating."
        ),
    )
    speech_chain = speech_prompt | llm | StrOutputParser()
    speech_result = speech_chain.invoke({"title": title_result})
    st.subheader("🗣️ Generated Speech")
    st.write(speech_result)

    # Step 3: Convert Speech to Audio using gTTS
    st.subheader("🔊 Listen to Speech")
    try:
        tts = gTTS(text=speech_result, lang="en")
        with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            f.seek(0)
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
