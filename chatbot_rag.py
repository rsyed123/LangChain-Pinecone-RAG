#import streamlit
import streamlit as st
import os
from dotenv import load_dotenv

# import pinecone
from pinecone import Pinecone, ServerlessSpec

# import langchain
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

st.title("Chatbot")

# ── Authentication ────────────────────────────────────────────────────────────
if not st.experimental_user.is_logged_in:
    st.info("Please sign in to use the chatbot.")
    if st.button("Sign in with Google"):
        st.login("google")
    st.stop()

with st.sidebar:
    st.write(f"Signed in as **{st.experimental_user.email}**")
    if st.button("Sign out"):
        st.logout()
# ─────────────────────────────────────────────────────────────────────────────

# initialize pinecone database
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# initialize pinecone database
index_name = os.environ.get("PINECONE_INDEX_NAME")  # change if desired
index = pc.Index(index_name)

# initialize embeddings model + vector store
embeddings = OpenAIEmbeddings(model="text-embedding-3-large",api_key=os.environ.get("OPENAI_API_KEY"))
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

print("Key loaded:", os.environ.get("OPENAI_API_KEY")[:10])


# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# create the bar where we can type messages
prompt = st.chat_input("How are you?")

# did the user submit a prompt?
if prompt:

    # add the message from the user (prompt) to the screen with streamlit
    with st.chat_message("user"):
        st.markdown(prompt)

        st.session_state.messages.append(HumanMessage(prompt))

    # creating and invoking the retriever
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5},
    )

    docs = retriever.invoke(prompt)

    if not docs:
        result = "I don't know."
    else:
        docs_text = "".join(d.page_content for d in docs)

        # creating the system prompt
        system_prompt = """You are a question-answering assistant.
Answer the question using ONLY the context provided below. Do not use any outside knowledge.
If the context does not contain the answer, say "I don't know." Do not guess or make up information.
Use three sentences maximum and keep the answer concise.
Context: {context}"""

        system_prompt_fmt = system_prompt.format(context=docs_text)

        print("-- SYS PROMPT --")
        print(system_prompt_fmt)

        # initialize the llm
        llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # invoking the llm with system prompt prepended fresh each turn
        result = llm.invoke([SystemMessage(system_prompt_fmt)] + st.session_state.messages).content

    # adding the response from the llm to the screen (and chat)
    with st.chat_message("assistant"):
        st.markdown(result)

        st.session_state.messages.append(AIMessage(result))

