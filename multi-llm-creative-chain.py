import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.title("Startup Idea Generator & Critique")

theme = st.text_input("Enter an industry or theme:", "sustainable travel")

idea_llm = ChatOpenAI(model="gpt-5-mini")
critic_llm = ChatOpenAI(model="gpt-5")

idea_prompt = PromptTemplate(
    input_variables=["theme"],
    template="Generate 5 innovative startup ideas in the {theme} industry."
)

critic_prompt = PromptTemplate(
    input_variables=["ideas"],
    template="Critically evaluate these startup ideas for feasibility and originality:\n{ideas}"
)

chain = (
    idea_prompt
    | idea_llm
    | StrOutputParser()
    | critic_prompt
    | critic_llm
    | StrOutputParser()
)

if st.button("Generate & Critique"):
    with st.spinner("Generating and analyzing ideas..."):
        result = chain.invoke({"theme": theme})
    st.subheader("Results:")
    st.write(result)
