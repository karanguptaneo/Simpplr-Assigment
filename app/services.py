import os
import fitz  # PyMuPDF for reading PDFs
import openai
from elasticsearch import Elasticsearch
from typing import List
from elastic_schema import elastic_schema_mapping

class DocumentHandler:
    """Handles loading, preprocessing, and indexing of policy documents."""
    
    def __init__(self, es_host: str, openai_key: str):
        openai.api_key = openai_key
        self.es = Elasticsearch(es_host)
        self.index_name = "policy_docs_"

    def load_documents(self, folder_path: str) -> List[str]:
        """Load and extract text from policy PDFs, breaking text into chunks after every 4th line 
        and ensuring each chunk has a reasonable number of characters."""
        chunks = []
        min_chars = 20  # Set a threshold for a reasonable number of characters

        for policy_file in os.listdir(folder_path):
            if policy_file.endswith(".pdf"):
                doc = fitz.open(os.path.join(folder_path, policy_file))
                for page in doc:
                    text = page.get_text("text")
                    if text not in ('', " ", "\n", "\t"):
                        lines = text.splitlines()  # Split text into lines
                        # Group lines into chunks of 4
                        for i in range(0, len(lines), 4):
                            chunk = "\n".join(lines[i:i+4])
                            # Ensure the chunk has a reasonable number of characters before appending
                            if len(chunk.strip()) >= min_chars:
                                chunks.append(chunk)

        return chunks

    def index_documents(self, chunks: List[str]):
        """Index document chunks into Elasticsearch with embeddings."""
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=elastic_schema_mapping)

        for i, chunk in enumerate(chunks):
            embedding = self.get_openai_embedding(chunk)
            print(len(embedding))
            
            self.es.index(index=self.index_name, id=i, body={
                "content": chunk,
                "embedding": embedding
            })

    @staticmethod
    def get_openai_embedding(text: str) -> List[float]:
        """Generate embeddings for a given text using OpenAI API."""
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']


class PolicyQAService:
    """Service for handling policy queries and generating responses."""
    
    def __init__(self, es_host: str, openai_key: str):
        openai.api_key = openai_key
        self.es = Elasticsearch(es_host)
        self.index_name = "policy_docs_"

    def search_relevant_chunks(self, query: str, top_n: int = 5) -> List[str]:
        """Search for relevant document chunks using Elasticsearch."""
        embedding = self.get_openai_embedding(query)
        search_body = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": embedding}
                    }
                }
            }
        }
        response = self.es.search(index=self.index_name, body=search_body)
        return [hit['_source']['content'] for hit in response['hits']['hits'][:top_n]]

    def generate_answer(self, query: str, documents: List[str]) -> str:
        """Generate an answer to the user's query using OpenAI."""
        context = "\n\n".join(documents)
        
        # Modified system prompt to act as a QA system for policies, including the context within it
        system_prompt = (
            f"You are a helpful assistant from Company Simpplr. Your role is to provide answers based on the following policy-related context:\n\n"
            f"{context}\n\n"
            "If the context does not contain relevant information to answer the query, suggest that the user reach out to Simpplr HR and display a fallback email like: "
            "'The answer to your question is not covered in the current policy documents. Please contact Simpplr HR at hr@simpplr.com for further assistance.'"
        )

        prompt = f"Question: {query}\nAnswer:"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0]['message']['content'].strip()

    @staticmethod
    def get_openai_embedding(text: str) -> List[float]:
        """Generate embeddings for a given text using OpenAI API."""
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
