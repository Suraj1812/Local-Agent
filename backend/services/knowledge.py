import json
from io import BytesIO
from typing import Any, Dict, List

from docx import Document as DocxDocument
from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from database.models import Document, DocumentChunk
from services.embedding import cosine_similarity, embed_text
from services.text_utils import chunk_text


async def extract_text(file: UploadFile) -> str:
    content = await file.read()
    name = (file.filename or "").lower()
    mime = file.content_type or ""

    if "pdf" in mime or name.endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if "wordprocessingml" in mime or name.endswith(".docx"):
        document = DocxDocument(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    return content.decode("utf-8", errors="ignore")


async def add_document(db: Session, file: UploadFile) -> Dict[str, Any]:
    text = await extract_text(file)
    document = Document(
        filename=file.filename or "upload",
        mime_type=file.content_type or "application/octet-stream",
        content=text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    chunks = chunk_text(text)
    for index, chunk in enumerate(chunks):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding_json=json.dumps(embed_text(chunk)),
            )
        )
    db.commit()
    return {"id": document.id, "filename": document.filename, "mime_type": document.mime_type, "chunks": len(chunks)}


def list_documents(db: Session) -> List[Dict[str, Any]]:
    rows = db.query(Document).order_by(Document.created_at.desc()).all()
    output = []
    for row in rows:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == row.id).count()
        output.append(
            {
                "id": row.id,
                "filename": row.filename,
                "mime_type": row.mime_type,
                "chunks": chunks,
                "created_at": row.created_at,
            }
        )
    return output


def search_knowledge(db: Session, query: str, limit: int = 6) -> List[Dict[str, Any]]:
    query_vector = embed_text(query)
    rows = db.query(DocumentChunk, Document).join(Document, Document.id == DocumentChunk.document_id).all()
    ranked = []
    for chunk, document in rows:
        score = cosine_similarity(query_vector, json.loads(chunk.embedding_json))
        if score > 0:
            ranked.append(
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "score": score,
                }
            )
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
