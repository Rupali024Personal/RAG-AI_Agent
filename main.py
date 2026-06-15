import logging
import shutil
from pathlib import Path

from click import prompt
from fastapi import FastAPI, UploadFile, File, HTTPException
import inngest
import inngest.fast_api
from dotenv import load_dotenv
import uuid
import os
import datetime
#from inngest.experimental import ai
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGQueryResult, RAGUpsertResult,RAGChunkAndSrc,RAGSearchResult
from google import genai

load_dotenv()

gemini_client=genai.Client(
api_key=os.getenv("GEMINI_API_KEY"),
)

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=os.getenv("IS_PRODUCTION"),
    signing_key=os.getenv("INNGEST_SIGNING_KEY"),
    event_key=os.getenv("INNGEST_EVENT_KEY"),
    serializer=inngest.PydanticSerializer()
)
@inngest_client.create_function(
    fn_id="RAG: Inngest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(
        limit=2, period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(hours=4),
        key="event.data.source_id",
    ),
)
async def rag_ingest_pdf(ctx:inngest.Context):
    def _load(ctx:inngest.Context) -> RAGChunkAndSrc:
        pdf_path=ctx.event.data["pdf_path"]
        source_id=ctx.event.data.get("source_id",pdf_path)
        chunks=load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks,source_id=source_id)

    def _upsert(chunks_and_src:RAGChunkAndSrc) -> RAGUpsertResult:
        chunks=chunks_and_src.chunks
        source_id=chunks_and_src.source_id
        vecs=embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL,f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads=[{"source":source_id,"text":chunks[i]} for i in range(len(chunks))]
        QdrantStorage().upsert(ids,vecs,payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run("load_and_chunk",lambda:_load(ctx),output_type=RAGChunkAndSrc)
    ingested=await ctx.step.run("embed-and-upsert",lambda:_upsert(chunks_and_src),output_type=RAGUpsertResult)
    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx:inngest.Context):
    def _search(question:str,top_k:int=5) -> RAGSearchResult:
        query_vec=embed_texts([question])[0]
        store=QdrantStorage()
        found=store.search(query_vec,top_k)
        return RAGSearchResult(contexts=found["contexts"],sources=found["sources"])

    question=ctx.event.data["question"]
    top_k= int(ctx.event.data.get("top_k",5))

    found = await ctx.step.run("embed-and-search",lambda:_search(question,top_k),output_type=RAGSearchResult)
    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )

    # adapter = ai.google.Adapter(
    #     auth_key=os.getenv("OPENAI_API_KEY"),
    #     model="gemini-2.5-flash"
    # )

    # res = await ctx.step.ai.infer(
    #     "llm-answer",
    #     adapter=adapter,
    #     body={
    #         "max_output_tokens": 1024,
    #         "temperature": 0.2,
    #         "messages": [
    #             {"role": "system", "content": "You answer questions using only the provided context."},
    #             {"role": "user", "content": user_content}
    #         ]
    #     }
    # )
    # answer = res["choices"][0]["message"]["content"].strip()

    res = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "You answer questions using only the provided context.",
            user_content
        ]
    )
    answer=res.text

    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}


app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    uploads_dir=Path("/tmp/uploads")
    uploads_dir.mkdir(parents=True,exist_ok=True)

    file_path=uploads_dir/f"{uuid.uuid4()}_{file.filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    await inngest_client.send(
        inngest.Event(
            name="rag/inngest_pdf",
            data={
                "pdf_path":str(file_path.resolve()),
                "source_id":file.filename,
            },
        )
    )
    return {"status":"In-progress","message":"Inngest triggered in background."}

@app.post("/query")
async def query_pdf(request: RAGQueryResult):
    try:
        query_vector=embed_texts([request.question])[0]
        store=QdrantStorage()
        found=store.search(query_vector,request.top_k)

        contexts=found["contexts"]
        sources=found["sources"]

        context_block ="\n\n".join(
            f"- {c}"
            for c in contexts
        )
        prompt= f"""
        USE ONLY the supplied context.
        
        Context:
        {context_block}
        
        Question:
        {request.question}
        
        Answer:
        """
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {
            "answer": response.text,
            "sources": sources,
            "num_contexts": len(contexts),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )





inngest.fast_api.serve(app,inngest_client,[rag_ingest_pdf,rag_query_pdf_ai])