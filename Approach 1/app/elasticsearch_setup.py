from services import DocumentHandler
import os
from elastic_schema import elastic_schema_mapping
def setup_elasticsearch():
    # Initialize the document handler
    doc_handler = DocumentHandler(es_host="http://elasticsearch:9200", openai_key=os.getenv("OPENAI_KEY"), elastic_schema_mapping = elastic_schema_mapping)
    
    # Load and index the policy documents
    chunks = doc_handler.load_documents("./data/policies/")
    doc_handler.index_documents(chunks)

if __name__ == "__main__":
    # Ensure OpenAI API key is set in the environment variables
    if "OPENAI_KEY" not in os.environ:
        raise EnvironmentError("Please set the OPENAI_KEY environment variable.")
    
    setup_elasticsearch()
