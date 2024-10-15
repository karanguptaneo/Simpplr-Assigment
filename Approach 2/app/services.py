from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.core import KnowledgeGraphIndex, StorageContext
# from llama_index.core.response_synthesis import ResponseSynthesizer
import fitz
import os
from pydantic import BaseModel, Field
from typing import List, Dict

class KnowledgeGraphService:
    def __init__(self):
        # Set up OpenAI API key and Neo4j credentials
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")
        self.llm = OpenAI(temperature=0)
        self.neo4j_url = "neo4j://neo4j:7687/"
        self.neo4j_username = os.getenv("neo4j_user")
        self.neo4j_password = os.getenv("neo4j_password")
        print(self.neo4j_username, self.neo4j_password)
        self.graph_store = Neo4jGraphStore(
            url=self.neo4j_url,
            username=self.neo4j_username,
            password=self.neo4j_password
        )

    # Load and split text data
    def load_and_split_text(self, folder_path: str) -> List[Document]:
        """Load and extract text from policy PDFs"""
        documents = []  # Store documents
        for policy_file in os.listdir(folder_path):
            if policy_file.endswith(".pdf"):
                file_path = os.path.join(folder_path, policy_file)
                with fitz.open(file_path) as doc:
                    text = ""
                    for page in doc:
                        text += page.get_text("text")
                    documents.append(Document(page_content=text, metadata={"source": file_path}))

        # Split documents
        text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
        split_documents = text_splitter.split_documents(documents)

        return split_documents 
    
    def extract_knowledge_graph(self, split_documents: List[Document]):
        llm_transformer = LLMGraphTransformer(llm=self.llm)
        return llm_transformer.convert_to_graph_documents(split_documents)

    # Store the extracted knowledge graph in Neo4j
    def store_knowledge_graph(self, graph_documents: List[Dict[str, str]]):
        # Assign a unique identifier to each document
        documents = []
        for i, doc in enumerate(graph_documents):
            new_doc = Document(page_content=doc.page_content)
            documents.append(new_doc)

        storage_context = StorageContext.from_defaults(graph_store=self.graph_store)
        KnowledgeGraphIndex.from_documents(documents, storage_context=storage_context)


    # Query the knowledge graph using a retriever
    def query_knowledge_graph(self, query: str) -> str:
        retriever = KnowledgeGraphRAGRetriever(storage_context=self.graph_store.storage_context, verbose=True)
        query_engine = RetrieverQueryEngine.from_args(retriever)
        retrieved_context = query_engine.query(query)
        # return str(retrieved_context)
        # response_synthesizer = ResponseSynthesizer()
        # return response_synthesizer.synthesize(query, retrieved_context)

    # Complete processing and querying
    def fill_knowledge_graph(self, folder_path: str):
        texts = self.load_and_split_text(folder_path)
        # graph_documents = self.extract_knowledge_graph(texts)
        self.store_knowledge_graph(texts)
