import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

title_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""You are an experienced speech writer.
    You need to craft an impactful title for a speech 
    on the following topic: {topic}
    Answer exactly one title.
    """
)

speech_prompt = PromptTemplate(
    input_variables=["title","emotion"],
    template="""You need to write a powerful {emotion} speech of 350 words
    for the following title: {title}
    Format the output with 2 keys: 'title', 'speech' and fill them with respective values
    """
)

first_chain = title_prompt | llm | StrOutputParser() | (lambda title: (st.write("title"), title)[1])
second_chain = speech_prompt | llm | JsonOutputParser()
##
#You can also do this instead of lambda
#def display_and_return_title(title):
#    st.write(title)  # Show it
#    return title     # Pass it along

# Instead of: (lambda title: (st.write(title), title)[1])
# Use: display_and_return_title
##
final_chain = first_chain | (lambda title:{"title":title,"emotion":emotion}) | second_chain

st.title("Speech Generator")
topic = st.text_input("Enter the topic:")
emotion = st.text_input("Enter the emotion:")

if topic:
    response = final_chain.invoke({"topic": topic})
    st.write(response)
