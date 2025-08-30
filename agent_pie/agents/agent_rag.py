from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import time
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from agent_pie.agents.agent_init import llm
from agent_pie.schemas.schemas import QueryRequest, QueryResponse

import shutil
from pathlib import Path
from langchain_community.vectorstores import Chroma


# ---------- Load environment variables ----------
load_dotenv()
hf_token = os.getenv("HF_TOKEN")


router = APIRouter(prefix="/api/v1/agent")

# ---------- Initialize models ----------
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question
    <context>
    {context}
    <context>
    Question: {input}
    """
)

vector_store = None


def create_vector_embedding():
    global vector_store
    loader = PyPDFDirectoryLoader("documents")  # Data ingestion
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs[:50])
    vector_store = Chroma.from_documents(final_documents, embeddings)


@router.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest):
    """Query the vector DB using RAG"""
    global vector_store
    if vector_store is None:
        raise HTTPException(
            status_code=400,
            detail="Vector database not initialized. Call /embed first.",
        )

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_store.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    response = retrieval_chain.invoke({"input": req.question})
    elapsed = time.process_time() - start

    return QueryResponse(answer=response["answer"], response_time=elapsed)


# Document upload

UPLOAD_DIR = Path("documents")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a research paper (PDF) and auto-create vector embeddings."""
    global vector_store

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save PDF into documents/
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        create_vector_embedding()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    return {"message": f"Uploaded {file.filename} and embeddings updated successfully"}
