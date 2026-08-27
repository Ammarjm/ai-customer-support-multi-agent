import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


KNOWLEDGE_BASE_PATH = "knowledge_base"
CHROMA_PATH = "chroma_db"


def load_documents():

    documents = []

    for file_name in os.listdir(KNOWLEDGE_BASE_PATH):

        if file_name.endswith(".pdf"):

            file_path = os.path.join(
                KNOWLEDGE_BASE_PATH,
                file_name
            )

            loader = PyPDFLoader(file_path)

            pdf_documents = loader.load()

            documents.extend(pdf_documents)

    return documents


def split_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def get_embedding_model():
    return embeddings


def create_vector_database(chunks):

    embeddings = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="company_knowledge"
    )

    return vector_store


def retrieve_documents(query, k=3):

    embeddings = get_embedding_model()

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="company_knowledge"
    )

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


def build_context(query):

    documents = retrieve_documents(query)

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    return context


def create_prompt(question, context):

    prompt = f"""
You are a customer support assistant for TechStore.

Answer the customer's question using ONLY
the provided company information.

If the answer is not available in the context,
say that you do not have enough information.

Context:
{context}

Customer Question:
{question}

Answer:
"""

    return prompt