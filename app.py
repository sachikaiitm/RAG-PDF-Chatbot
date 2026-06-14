import streamlit as st
from dotenv import load_dotenv

from src.ingest import load_pdf, chunk_documents
from src.vectorstore import create_vectorstore
from src.rag import retrieve_docs, generate_answer

load_dotenv()

st.set_page_config(
    page_title="RAG PDF Chatbot",
    page_icon="📄",
    layout="wide"
)

# -----------------------
# Session State
# -----------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# -----------------------
# UI
# -----------------------

st.markdown(
    """
    # 📄 RAG PDF Chatbot
    ##### by *Sachika J*
    """
)
st.write("Upload PDF documents and chat with them!")

# -----------------------
# Sidebar
# -----------------------

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)
current_files = (
    tuple(file.name for file in uploaded_files)
    if uploaded_files
    else ()
)

if "uploaded_files_key" not in st.session_state:
    st.session_state.uploaded_files_key = None

if current_files != st.session_state.uploaded_files_key:
    st.session_state.vectorstore = None
    st.session_state.uploaded_files_key = current_files

if uploaded_files:
    st.sidebar.success(
        f"{len(uploaded_files)} file(s) uploaded"
    )

# -----------------------
# Build Vector Database
# -----------------------

if uploaded_files and st.session_state.vectorstore is None:

    all_docs = []

    for uploaded_file in uploaded_files:
        docs = load_pdf(uploaded_file)
        all_docs.extend(docs)

    chunks = chunk_documents(all_docs)

    with st.spinner("Creating vector database..."):
        st.session_state.vectorstore = create_vectorstore(
            chunks
        )

    with st.expander("System Info"):

        st.write(
            f"Loaded {len(all_docs)} pages"
        )

        st.write(
            f"Created {len(chunks)} chunks"
        )

        st.success(
            "Vector database created!"
        )
# -----------------------
# Chat History
# -----------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if (
            message["role"] == "assistant"
            and "sources" in message
        ):

            with st.expander("Sources"):

                for source in message["sources"]:

                    st.write(source)

# -----------------------
# Chat Input
# -----------------------

question = st.chat_input(
    "Ask a question about your documents..."
)

# -----------------------
# New Question
# -----------------------

if (
    uploaded_files
    and st.session_state.vectorstore
    and question
):

    # User Message

    with st.chat_message("user"):
        st.write(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Assistant Message

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        message_placeholder.write(
            "🔍 Searching documents..."
        )

        retrieved_docs = retrieve_docs(
            st.session_state.vectorstore,
            question
        )

        message_placeholder.write(
            "🤖 Generating answer..."
        )

        answer = generate_answer(
            question,
            retrieved_docs
        )

        message_placeholder.empty()

        st.write(answer)

        source_list = []

        with st.expander("Sources"):

            for doc in retrieved_docs:

                source_file = doc.metadata.get(
                    "source_file",
                    "Unknown File"
                )

                page_num = (
                    doc.metadata.get(
                        "page",
                        0
                    ) + 1
                )

                source_text = (
                    f"📄 {source_file} | Page {page_num}"
                )

                source_list.append(
                    source_text
                )

                st.write(source_text)

                st.write(
                    doc.page_content[:300]
                )

                st.divider()

        with st.expander(
            "Retrieved Chunks (Debug)"
        ):

            for i, doc in enumerate(
                retrieved_docs
            ):

                st.write(
                    f"Chunk {i + 1}"
                )

                st.write(
                    doc.page_content
                )

                st.divider()

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": source_list
        }
    )