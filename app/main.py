from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # To define request body structure
from app.services import PolicyQAService
import os

app = FastAPI()

# Initialize the PolicyQAService
qa_service = PolicyQAService(es_host="http://elasticsearch:9200", openai_key=os.getenv("OPENAI_KEY"))

# Define a request body model using Pydantic
class QueryRequest(BaseModel):
    user_query: str  # This defines the required field for the query

@app.post("/ask_policy/")
async def ask_policy(request: QueryRequest):  # Use the Pydantic model
    try:
        # Extract the user query from the request object
        user_query = request.user_query
        # Search for relevant document chunks using Elasticsearch
        relevant_chunks = qa_service.search_relevant_chunks(user_query)
        # Use OpenAI to generate a precise answer based on the retrieved chunks
        answer = qa_service.generate_answer(user_query, relevant_chunks)

    return {"response": answer, "sources": relevant_chunks}

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
