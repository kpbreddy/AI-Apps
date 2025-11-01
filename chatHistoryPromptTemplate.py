import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#from travelapp_demo import prompt_template

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-5",api_key=OPENAI_API_KEY)
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a Agile coach. Answer any questions"
         "related to agile process"),
        ("user", "{input}")
    ]
)

st.title("Agile Guide")

input = st.text_input("Enter the question:")

chain = prompt_template | llm

if input:
    response = chain.invoke({"input": input})
    st.write(response.content)
