def retrieve_docs(vectorstore, query):

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 20
        }
    )   

    docs = retriever.invoke(query)

    return docs

from langchain_groq import ChatGroq


def generate_answer(question, docs):

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
    You are a document question-answering assistant.

    Answer ONLY from the provided context.

    If the answer is not explicitly stated in the context,
    reply:

    "I cannot find the answer in the retrieved context."

    Do not make assumptions.
    Do not infer facts.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    llm = ChatGroq(
        model="llama-3.3-70b-versatile"
    )

    response = llm.invoke(prompt)

    return response.content