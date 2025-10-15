import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found in environment variables.")
    st.stop()

llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

title_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""
    You are an experienced chef-cook.
    You need to find the favourite recipe based
    on the following topic: {topic}
    Answer exactly with one title.
    """
)

speech_prompt = PromptTemplate(
    input_variables=["title"],
    template="""
    You need to write a recipe of about 100 words
    for the following title: {title}
    """
)

first_chain = title_prompt | llm | StrOutputParser()
second_chain = speech_prompt | llm | StrOutputParser()

st.title("Cuisine Recipe App")
topic = st.text_input("Enter the country:")

if topic:
    # Generate title
    title = first_chain.invoke({"topic": topic})
    st.subheader(f"🍽️ {title}")

    # Generate recipe
    recipe = second_chain.invoke({"title": title})
    st.write(recipe)
