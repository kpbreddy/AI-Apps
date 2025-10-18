import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.title("💡 Startup Idea Generator & Critique")

# --- User Inputs ---
theme = st.text_input("Enter an industry or theme:", "sustainable travel")

st.sidebar.header("⚙️ Model Parameters")
temperature = st.sidebar.slider("Temperature (creativity)", 0.0, 2.0, 0.7, 0.1)
top_p = st.sidebar.slider("Top P (nucleus sampling)", 0.0, 1.0, 1.0, 0.05)
top_k = st.sidebar.slider("Top K (token sampling limit)", 1, 100, 50, 1)
max_tokens = st.sidebar.number_input("Max Tokens", min_value=50, max_value=2000, value=300, step=50)

# --- LLM Setup ---
idea_llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=temperature,
    top_p=top_p,
    top_k=top_k,
    max_tokens=max_tokens
)

critic_llm = ChatOpenAI(
    model="gpt-5",
    temperature=temperature,
    top_p=top_p,
    top_k=top_k,
    max_tokens=max_tokens
)

# --- Prompts ---
idea_prompt = PromptTemplate(
    input_variables=["theme"],
    template="Generate 5 innovative startup ideas in the {theme} industry."
)

critic_prompt = PromptTemplate(
    input_variables=["ideas"],
    template="Critically evaluate these startup ideas for feasibility and originality:\n{ideas}"
)

# --- Chain ---
chain = (
    idea_prompt
    | idea_llm
    | StrOutputParser()
    | critic_prompt
    | critic_llm
    | StrOutputParser()
)

# --- Run ---
if st.button("🚀 Generate & Critique"):
    with st.spinner("Generating and analyzing ideas..."):
        result = chain.invoke({"theme": theme})
    st.subheader("🧾 Results:")
    st.write(result)
