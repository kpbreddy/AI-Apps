import os
from langchain_aws import ChatBedrock
import streamlit as st
from langchain.prompts import PromptTemplate

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)
prompt_template = PromptTemplate(
    input_variables = ["skills","industry"],
    template = """
    I am an entrepreneur with skills in {skills} interested in {industry}.
    Generate 3 startup ideas that solve real-world problems, each with:
    - Idea name
    - Problem solved
    - Solution outline
    - Monetization model
    - Tech stack suggestion
    """
)

st.title("AI Startup Ideator")

skills = st.text_input("Enter the skills")
industry = st.text_input("Enter the industry")
if skills:
    response = llm.invoke(prompt_template.format(skills=skills,
                                                 industry=industry
                                                 ))
    st.write(response.content)
    print(response)
