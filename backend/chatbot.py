from fastapi import APIRouter, UploadFile, HTTPException
from pdf_reader import extract_text_from_pdf
from text_splitter import split_text
from vector_store import reset_store, add_documents, get_context
from llm_engine import generate_answer

router = APIRouter()

@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile):
    text = extract_text_from_pdf(file.file)

    if not text.strip():
        raise HTTPException(400, "PDF has no readable text.")

    reset_store()
    chunks = split_text(text)
    add_documents(chunks)

    return {"message": "PDF processed", "chunks": len(chunks)}

@router.get("/ask")
async def ask_question(q: str):
    context = get_context(q, top_k=5)

    if not context:
        return {"answer": "No relevant information found in PDF."}

    ans = generate_answer(context, q)
    return {"answer": ans}

