from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # To define request body structure
from app.services import KnowledgeGraphService  # Import the new service
import os

app = FastAPI()

# Initialize the KnowledgeGraphService
kg_service = KnowledgeGraphService()

# Define a request body model using Pydantic
class QueryRequest(BaseModel):
    user_query: str  # This defines the required field for the query

@app.post("/ask_policy/")
async def ask_policy(request: QueryRequest):  # Use the Pydantic model
    # try:
    # Extract the user query from the request object
    user_query = request.user_query
    # Use KnowledgeGraphService to retrieve relevant context
    relevant_context = kg_service.query_knowledge_graph(user_query)
    # Use OpenAI to generate a precise answer based on the retrieved context
    answer = kg_service.generate_answer(user_query, relevant_context)

    return {"response": answer, "sources": {}}

    # except Exception as e:
    #     print(str(e))
    #     raise HTTPException(status_code=500, detail=str(e))
