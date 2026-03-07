import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=os.environ.get("OPENAI_API_KEY"),
)
vector_store = PineconeVectorStore(index=index, embedding=embeddings)
llm = ChatOpenAI(model="gpt-4o", temperature=1)


def get_rag_response(messages: list[dict]) -> str:
    # Use the last user message for retrieval
    user_message = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5},
    )
    docs = retriever.invoke(user_message)
    docs_text = "".join(d.page_content for d in docs)

    system_prompt = f"""You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.
Context: {docs_text}"""

    lc_messages = [SystemMessage(system_prompt)]
    for m in messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(m["content"]))
        elif m["role"] == "assistant":
            lc_messages.append(AIMessage(m["content"]))

    return llm.invoke(lc_messages).content
