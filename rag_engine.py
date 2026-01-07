import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, OllamaEmbeddings

CONTENT_DIR = "Content"


def load_markdown_files():
    documents = []

    for file in os.listdir(CONTENT_DIR):
        if file.endswith(".md"):
            path = os.path.join(CONTENT_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": file}
                )
            )

    return documents


def build_rag():
    raw_docs = load_markdown_files()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.split_documents(raw_docs)

    embeddings = OllamaEmbeddings(model="mistral")
    vectorstore = FAISS.from_documents(docs, embeddings)

    retriever = vectorstore.as_retriever()
    llm = OllamaLLM(model="mistral", temperature=0)

    return retriever, llm


def ask_question(query, retriever, llm):
    docs = retriever.invoke(query)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = (
        "You are a beginner-friendly Python tutor.\n"
        "Explain clearly with examples.\n\n"
        "Context:\n"
        f"{context}\n\n"
        "Question:\n"
        f"{query}\n"
    )

    return llm.invoke(prompt)
